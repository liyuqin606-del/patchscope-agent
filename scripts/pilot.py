"""Public HumanEval execution pilot, not a held-out repository benchmark.

Fixed first five tasks; canonical vs deliberately simple return-None mutants.
One task-only test-generation request per task is shared across both candidates.
No reference implementation or hidden test enters a provider payload.
"""
import ast
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from patchscope.provider import BudgetClient
from patchscope.checks import run_container
from patchscope.evaluation import score

ROOT = Path(__file__).resolve().parents[1]


def execute(source, trailer, image):
    with tempfile.TemporaryDirectory(prefix='patchscope-pilot-') as name:
        root = Path(name)
        root.chmod(0o755)
        script = root / 'runner.py'
        script.write_text(source + '\n' + trailer)
        script.chmod(0o644)
        result = run_container(root, image, ['python', '-B', 'runner.py'], timeout=15)
        if result['status'] != 'pass':
            return {'status': 'error', 'detail': result}
        try:
            return json.loads(result['output'].splitlines()[-1])
        except (KeyError, ValueError, IndexError):
            return {'status': 'error', 'detail': 'missing structured runner output'}


def main():
    image = json.loads(subprocess.check_output(['docker', 'image', 'inspect', 'python:3.12-slim']))[0]['RepoDigests'][0]
    tasks = [json.loads(line) for line in gzip.decompress((ROOT/'data/HumanEval.jsonl.gz').read_bytes()).splitlines()][:5]
    client = BudgetClient(ROOT/'.env', ROOT/'reports/api-ledger.jsonl')
    report = {'stage': 'development_execution_pilot', 'image': image,
              'dataset_commit': '6d43fb980f9fee3c892a914eda09951f772ad10d',
              'dataset_sha256': hashlib.sha256((ROOT/'data/HumanEval.jsonl.gz').read_bytes()).hexdigest(),
              'selection': 'first five tasks; canonical and return-None mutant per task', 'tasks': []}
    labels, generated, static = [], [], []
    output = ROOT/'reports/execution-pilot.json'
    for task in tasks:
        task_id = task['task_id']
        correct = task['prompt'] + task['canonical_solution']
        wrong = task['prompt'] + '    return None\n'
        hidden = task['test'] + f'''\nimport json
try:
    check({task['entry_point']})
    print(json.dumps({{"status":"pass"}}))
except AssertionError:
    print(json.dumps({{"status":"fail"}}))
except Exception as e:
    print(json.dumps({{"status":"error","type":type(e).__name__}}))
'''
        ground = [execute(source, hidden, image) for source in (correct, wrong)]
        if [r['status'] for r in ground] != ['pass', 'fail']:
            report['tasks'].append({'id': task_id, 'excluded': 'ground-truth qualification failed', 'ground_truth': ground})
            output.write_text(json.dumps(report, indent=2))
            continue
        response = client.call([
            {'role': 'system', 'content': 'Generate discriminating tests from the supplied Python function contract. '
             'Return ONLY a JSON object with key cases, a list of 3 to 6 objects with args (JSON list of positional arguments) '
             'and expected (JSON value). Include ordinary, boundary, and counterexample cases. No Python code or markdown.'},
            {'role': 'user', 'content': task['prompt']}], max_tokens=1400)
        content = response['choices'][0]['message']['content']
        try:
            tests = json.loads(content)
            assert 3 <= len(tests['cases']) <= 6
            assert all(isinstance(c['args'], list) and 'expected' in c for c in tests['cases'])
        except (ValueError, AssertionError, KeyError, TypeError):
            tests = None
        entry = {'id': task_id, 'raw_model_content': content, 'usage': response.get('usage'),
                 'finish_reason': response['choices'][0].get('finish_reason'), 'ground_truth': ground, 'candidates': []}
        for kind, source, is_correct in [('canonical', correct, True), ('mutant', wrong, False)]:
            case_id = task_id + '/' + kind
            labels.append({'id': case_id, 'correct': is_correct})
            ast.parse(source)
            static.append({'id': case_id, 'verdict': 'insufficient_evidence'})
            if tests is None:
                result = {'status': 'error', 'detail': 'invalid model test schema'}
            else:
                trailer = '''import json, math
cases = json.loads(TESTS)
def equal(a,b):
    if isinstance(a,bool) or isinstance(b,bool): return type(a) is type(b) and a == b
    if isinstance(a,(int,float)) and isinstance(b,(int,float)): return math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-9)
    if isinstance(a,list) and isinstance(b,list): return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
    return a == b
observations=[]
for c in cases:
    try:
        actual=FUNCTION(*c['args'])
        observations.append({'pass':equal(actual,c['expected']), 'actual':actual, 'expected':c['expected']})
    except Exception as e:
        observations.append({'pass':False,'exception':type(e).__name__})
print(json.dumps({'status':'pass' if all(c['pass'] for c in observations) else 'fail','cases':observations}))
'''.replace('TESTS', repr(json.dumps(tests['cases']))).replace('FUNCTION', task['entry_point'])
                result = execute(source, trailer, image)
            verdict = {'pass': 'insufficient_evidence', 'fail': 'reject', 'error': 'error'}[result['status']]
            generated.append({'id': case_id, 'verdict': verdict})
            entry['candidates'].append({'kind':kind, 'candidate_sha256':hashlib.sha256(source.encode()).hexdigest(),
                                        'verdict':verdict, 'execution':result})
        report['tasks'].append(entry)
        report['scores'] = {'syntax':score(labels, static), 'generated_tests':score(labels, generated)}
        output.write_text(json.dumps(report, indent=2) + '\n')
        print(task_id, [(c['kind'],c['verdict']) for c in entry['candidates']], flush=True)
    print(json.dumps(report.get('scores', {}), indent=2))


if __name__ == '__main__':
    main()
