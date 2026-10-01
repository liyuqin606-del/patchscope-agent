"""Non-executing checks and a fail-closed, container-only execution boundary."""
import ast
import subprocess
from pathlib import Path


def syntax_check(source: str) -> dict:
    try:
        ast.parse(source)
        return {'check': 'python_syntax', 'status': 'pass', 'scope': 'syntax only'}
    except SyntaxError as exc:
        return {'check': 'python_syntax', 'status': 'fail', 'line': exc.lineno, 'detail': exc.msg}


def run_container(root: Path, image: str, command: list[str], timeout: int = 30) -> dict:
    """Run a prepared repository snapshot, never arbitrary commands on the host.

    Image must be preloaded and pinned by digest. Docker is a development
    isolation boundary, not a guarantee for hostile multi-tenant workloads.
    """
    if '@sha256:' not in image or not command:
        raise ValueError('A digest-pinned image and explicit argv are required')
    import uuid
    name = 'patchscope-' + uuid.uuid4().hex
    argv = ['docker', 'run', '--name', name, '--rm', '--pull=never', '--network=none',
            '--read-only', '--cap-drop=ALL', '--security-opt=no-new-privileges',
            '--pids-limit=64', '--memory=512m', '--cpus=1', '--user=65534:65534',
            '--tmpfs', '/tmp:rw,noexec,nosuid,size=64m',
            '--mount', f'type=bind,src={root.resolve()},dst=/workspace,readonly',
            '--workdir', '/workspace', image, *command]
    # File-backed output avoids unbounded PIPE memory; report is truncated.
    import tempfile
    try:
        with tempfile.TemporaryFile() as output:
            proc = subprocess.run(argv, stdout=output, stderr=output, timeout=timeout)
            output.seek(0)
            text = output.read(16_384).decode(errors='replace')
        return {'status': 'pass' if proc.returncode == 0 else 'error',
                'returncode': proc.returncode, 'output': text}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {'status': 'unavailable', 'detail': type(exc).__name__}
    finally:
        try:
            subprocess.run(['docker', 'rm', '-f', name], capture_output=True, timeout=5)
        except (OSError, subprocess.TimeoutExpired):
            pass


def behavioral_check(source: str, entry_point: str, cases: list[dict], image: str) -> dict:
    """Execute JSON input/output cases in the pinned container.

    Expected outputs are proposed evidence, not ground truth. A failed case can
    reflect a bad test; preserve it for independent scoring of false rejections.
    """
    import json
    import tempfile
    if not entry_point.isidentifier() or not 1 <= len(cases) <= 8:
        raise ValueError('Invalid entry point or case count')
    if any(not isinstance(case.get('args'), list) or 'expected' not in case for case in cases):
        raise ValueError('Each case requires positional args and expected value')
    serialized = json.dumps(cases, allow_nan=False)
    if len(serialized) > 16_000:
        raise ValueError('Test cases exceed size budget')
    trailer = '''
import json, math
_test_cases=json.loads(TESTS)
def _equal(a,b):
    if isinstance(a,bool) or isinstance(b,bool): return type(a) is type(b) and a==b
    if isinstance(a,(int,float)) and isinstance(b,(int,float)): return math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-9)
    if isinstance(a,list) and isinstance(b,list): return len(a)==len(b) and all(_equal(x,y) for x,y in zip(a,b))
    return a==b
_observations=[]
for _case in _test_cases:
    try:
        _actual=FUNCTION(*_case['args'])
        _observations.append({'pass':_equal(_actual,_case['expected']),'actual':_actual,'expected':_case['expected']})
    except Exception as _error:
        _observations.append({'pass':False,'exception':type(_error).__name__})
print(json.dumps({'status':'pass' if all(c['pass'] for c in _observations) else 'fail','cases':_observations}))
'''.replace('TESTS', repr(serialized)).replace('FUNCTION', entry_point)
    with tempfile.TemporaryDirectory(prefix='patchscope-check-') as name:
        root = Path(name)
        root.chmod(0o755)
        script = root/'runner.py'
        script.write_text(source + '\n' + trailer)
        script.chmod(0o644)
        result = run_container(root, image, ['python', '-B', 'runner.py'], timeout=15)
    if result['status'] != 'pass':
        return {'check': 'generated_cases', 'status': 'error', 'execution': result}
    try:
        observed = json.loads(result['output'].splitlines()[-1])
        if observed.get('status') not in {'pass', 'fail'} or not isinstance(observed.get('cases'), list):
            raise ValueError('Missing structured test observations')
        return {'check':'generated_cases', **observed, 'scope':'model-proposed expected values; not an oracle'}
    except (ValueError, IndexError, AttributeError):
        return {'check':'generated_cases','status':'error','detail':'invalid runner output'}
