"""Rebuild a readable report from raw experiment records, without model calls."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',default='adaptive-comparison.json')
    parser.add_argument('--output',default='EXPERIMENT_REPORT.md')
    args=parser.parse_args()
    path=ROOT/'reports'/args.input
    report=json.loads(path.read_text())
    ledger=[json.loads(line) for line in (ROOT/'reports/api-ledger.jsonl').read_text().splitlines()]
    lines=['# PatchScope development experiment report', '',
           '**Scope:** public HumanEval tasks with programmatically constructed operator mutations. '
           'This is not a repository-disjoint final benchmark, and public tasks may be in model training data.', '',
           '## Protocol', '',
           f"- Seed tasks: {report['seed_tasks']}; qualified tasks: {report.get('included_tasks','run incomplete')}; "
           f"excluded: {report.get('excluded_tasks','run incomplete')}.",
           '- Each qualified task contributes a canonical candidate and one operator mutant.',
           '- Fixed and adaptive conditions see identical contracts/candidates and receive two calls, each capped at 1,200 output tokens.',
           '- Fixed generates both batches before execution. Adaptive observes the first batch outcome before its second request.',
           '- Correct candidates and hidden scoring tests never appear together in a model prompt; hidden scoring tests are local only.',
           '- A passing generated suite yields insufficient evidence, not a correctness guarantee.',
           '- Temperature is zero, with one run per condition. Provider nondeterminism and ordering remain limitations.',
           '', '## Results', '',
           '| Condition | Wrong detected | Correct falsely rejected | Errors |',
           '|---|---:|---:|---:|']
    for name,s in report.get('scores',{}).items():
        lines.append(f"| {name} | {s['detected']}/{s['wrong_count']} | {s['false_rejections']}/{s['correct_count']} | {s['verdict_counts'].get('error',0)} |")
    lines += ['', 'No superiority claim is inferred from this small development run. '
              'Descriptive Wilson intervals are in the JSON; they are not repository-clustered inference.',
              '', '## Exclusions', '']
    for task in report['tasks']:
        if 'excluded' in task:
            lines.append(f"- {task['id']}: {task['excluded']}; qualification: `{json.dumps(task.get('qualification'))}`")
    lines += ['', '## Correct-candidate rejection cases', '']
    for task in report['tasks']:
        for run in task['runs']:
            if run['candidate']=='canonical' and run.get('verdict')=='reject':
                failed=[]
                for round in run['rounds']:
                    for i,c in enumerate(round.get('execution',{}).get('cases',[])):
                        if not c['pass']:
                            failed.append({'input':round.get('cases',[])[i], 'observation':c})
                lines.append(f"- {task['id']}, {run['condition']}: `{json.dumps(failed)}`")
    lines += ['', '## Cost accounting', '',
              f"All project API requests so far: {len(ledger)}. "
              f"List-price usage estimate: {sum(r.get('estimated_cny',0) for r in ledger):.6f} CNY. "
              f"Conservative reservations: {sum(r['reserved_cny'] for r in ledger):.6f} CNY.",
              'Includes connectivity checks and the earlier execution pilot. Account billing may differ; this is not an invoice.',
              'Internal reservation ceiling: 15 CNY, below the user-authorized 18 CNY. Requests are serialized, have no retries, '
              'and retain reservations on errors.', '', '## Reproduction', '',
              'Dependencies are locked in `uv.lock`. Input data is pinned to HumanEval commit '
              '`6d43fb980f9fee3c892a914eda09951f772ad10d`; Docker image digest is recorded in JSON.',
              'Run `uv run python scripts/summarize.py` to regenerate this report without paid calls.',
              'Run `uv run python scripts/compare.py` only for a new explicitly budgeted run; '
              'it refuses to overwrite the existing artifact.', '']
    (ROOT/'reports'/args.output).write_text('\n'.join(lines))
    print('reports/'+args.output)


if __name__=='__main__': main()
