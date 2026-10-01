# PatchScope development experiment report

**Scope:** public HumanEval tasks with programmatically constructed operator mutations. This is not a repository-disjoint final benchmark, and public tasks may be in model training data.

## Protocol

- Seed tasks: 15; qualified tasks: 8; excluded: 7.
- Each qualified task contributes a canonical candidate and one operator mutant.
- Fixed and adaptive conditions see identical contracts/candidates and receive two calls, each capped at 1,200 output tokens.
- Fixed generates both batches before execution. Adaptive observes the first batch outcome before its second request.
- Correct candidates and hidden scoring tests never appear together in a model prompt; hidden scoring tests are local only.
- A passing generated suite yields insufficient evidence, not a correctness guarantee.
- Temperature is zero, with one run per condition. Provider nondeterminism and ordering remain limitations.

## Results

| Condition | Wrong detected | Correct falsely rejected | Errors |
|---|---:|---:|---:|
| fixed | 6/8 | 2/8 | 4 |
| adaptive | 8/8 | 2/8 | 1 |

No superiority claim is inferred from this small development run. Descriptive Wilson intervals are in the JSON; they are not repository-clustered inference.

## Exclusions

- HumanEval/2: no eligible operator; qualification: `null`
- HumanEval/5: no eligible operator; qualification: `null`
- HumanEval/7: no eligible operator; qualification: `null`
- HumanEval/8: no eligible operator; qualification: `null`
- HumanEval/9: no eligible operator; qualification: `null`
- HumanEval/10: mutation not distinguished by scoring tests or infrastructure error; qualification: `[{"status": "pass"}, {"status": "error", "detail": {"status": "unavailable", "detail": "TimeoutExpired"}}]`
- HumanEval/13: no eligible operator; qualification: `null`

## Correct-candidate rejection cases

- HumanEval/0, fixed: `[{"input": {"args": [[5.0, 3.0, 1.0], 1.5], "expected": true}, "observation": {"pass": false, "actual": false, "expected": true}}, {"input": {"args": [[5.0, 3.0, 1.0], 1.5], "expected": true}, "observation": {"pass": false, "actual": false, "expected": true}}]`
- HumanEval/4, adaptive: `[{"input": {"args": [[10.0, 20.0, 30.0]], "expected": 10.0}, "observation": {"pass": false, "actual": 6.666666666666667, "expected": 10.0}}, {"input": {"args": [[10.0, 20.0, 30.0]], "expected": 10.0}, "observation": {"pass": false, "actual": 6.666666666666667, "expected": 10.0}}]`
- HumanEval/6, fixed: `[{"input": {"args": ["((( )))"], "expected": [3]}, "observation": {"pass": false, "actual": [3, 0], "expected": [3]}}, {"input": {"args": ["((( )))"], "expected": [3]}, "observation": {"pass": false, "actual": [3, 0], "expected": [3]}}]`
- HumanEval/6, adaptive: `[{"input": {"args": ["((( )))"], "expected": [3]}, "observation": {"pass": false, "actual": [3, 0], "expected": [3]}}]`

## Cost accounting

All project API requests so far: 124. List-price usage estimate: 0.146563 CNY. Conservative reservations: 0.827038 CNY.
Includes connectivity checks and the earlier execution pilot. Account billing may differ; this is not an invoice.
Internal reservation ceiling: 15 CNY, below the user-authorized 18 CNY. Requests are serialized, have no retries, and retain reservations on errors.

## Reproduction

Dependencies are locked in `uv.lock`. Input data is pinned to HumanEval commit `6d43fb980f9fee3c892a914eda09951f772ad10d`; Docker image digest is recorded in JSON.
Run `uv run python scripts/summarize.py` to regenerate this report without paid calls.
Run `uv run python scripts/compare.py` only for a new explicitly budgeted run; it refuses to overwrite the existing artifact.
