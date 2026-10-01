"""CLI entrypoints. Default demo performs no paid API calls or code execution."""
import argparse
import json
from pathlib import Path
from .agent import run
from .evolution import Policy, select


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    review = commands.add_parser('review')
    review.add_argument('--repo', type=Path, required=True)
    review.add_argument('--candidate', type=Path, required=True)
    review.add_argument('--task', required=True)
    review.add_argument('--db', type=Path, default=Path('runs/checkpoints.db'))
    review.add_argument('--output', type=Path, default=Path('runs/report.json'))
    review.add_argument('--model', help='Explicit LangChain provider:model; may incur API costs')
    review.add_argument('--budget', type=int, default=4)
    review.add_argument('--image', help='Enable behavioral checks with a preloaded digest-pinned Docker image')
    review.add_argument('--api-env', type=Path, help='Use the budgeted compatible API client')
    review.add_argument('--ledger', type=Path, default=Path('reports/api-ledger.jsonl'))
    evolve = commands.add_parser('evolve-demo')
    evolve.add_argument('--records', type=Path, required=True)
    evolve.add_argument('--output', type=Path, default=Path('runs/evolution.json'))
    args = parser.parse_args()
    if args.command == 'review':
        result = run(args.repo, args.candidate, args.task, args.db, args.model, args.budget, args.api_env, args.ledger, args.image)
    else:
        rows = json.loads(args.records.read_text())
        result = select([Policy('syntax', ('syntax',)), Policy('syntax_contract', ('syntax', 'contract'))],
                        rows, Policy('syntax', ('syntax',)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k in {'verdict', 'mode', 'policy', 'promoted', 'limitation'}}, indent=2))
    print(f'Report: {args.output}')


if __name__ == '__main__':
    main()
