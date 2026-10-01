# PatchScope development experiment report

**Scope:** public HumanEval tasks with programmatically constructed operator mutations. This is not a repository-disjoint final benchmark, and public tasks may be in model training data.

## Protocol

- Seed tasks: 15; qualified tasks: 6; excluded: 9.
- Each qualified task contributes a canonical candidate and one operator mutant.
- Fixed and adaptive conditions see identical contracts/candidates and receive two calls, each capped at 1,200 output tokens.
- Fixed generates both batches before execution. Adaptive observes the first batch outcome before its second request.
- Correct candidates and hidden scoring tests never appear together in a model prompt; hidden scoring tests are local only.
- A passing generated suite yields insufficient evidence, not a correctness guarantee.
- Temperature is zero, with one run per condition. Provider nondeterminism and ordering remain limitations.

## Results

| Condition | Wrong detected | Correct falsely rejected | Errors |
|---|---:|---:|---:|
| fixed | 6/6 | 3/6 | 0 |
| adaptive | 6/6 | 4/6 | 0 |

No superiority claim is inferred from this small development run. Descriptive Wilson intervals are in the JSON; they are not repository-clustered inference.

## Exclusions

- HumanEval/16: no eligible operator; qualification: `null`
- HumanEval/17: no eligible operator; qualification: `null`
- HumanEval/19: no eligible operator; qualification: `null`
- HumanEval/22: no eligible operator; qualification: `null`
- HumanEval/23: no eligible operator; qualification: `null`
- HumanEval/25: mutation not distinguished by scoring tests or infrastructure error; qualification: `[{"status": "pass"}, {"status": "pass"}]`
- HumanEval/27: no eligible operator; qualification: `null`
- HumanEval/28: no eligible operator; qualification: `null`
- HumanEval/29: no eligible operator; qualification: `null`

## Correct-candidate rejection cases

- HumanEval/20, fixed: `[{"input": {"args": [[1.0, 2.0, 3.0, 4.0, 5.0, 2.2]], "expected": [2.0, 2.2]}, "observation": {"pass": false, "actual": [2.0, 2.2], "expected": [2.0, 2.2]}}, {"input": {"args": [[1.0, 2.0, 3.0, 4.0, 5.0, 2.0]], "expected": [2.0, 2.0]}, "observation": {"pass": false, "actual": [2.0, 2.0], "expected": [2.0, 2.0]}}, {"input": {"args": [[5.5, 1.1, 3.3, 2.2]], "expected": [1.1, 2.2]}, "observation": {"pass": false, "actual": [2.2, 3.3], "expected": [1.1, 2.2]}}, {"input": {"args": [[10.0, 10.1, 10.2, 10.3]], "expected": [10.0, 10.1]}, "observation": {"pass": false, "actual": [10.0, 10.1], "expected": [10.0, 10.1]}}, {"input": {"args": [[-1.0, -2.0, -3.0, -4.0]], "expected": [-4.0, -3.0]}, "observation": {"pass": false, "actual": [-2.0, -1.0], "expected": [-4.0, -3.0]}}, {"input": {"args": [[0.0, 0.0, 1.0]], "expected": [0.0, 0.0]}, "observation": {"pass": false, "actual": [0.0, 0.0], "expected": [0.0, 0.0]}}, {"input": {"args": [[1.0, 2.0, 3.0, 4.0, 5.0, 2.2]], "expected": [2.0, 2.2]}, "observation": {"pass": false, "actual": [2.0, 2.2], "expected": [2.0, 2.2]}}, {"input": {"args": [[1.0, 2.0, 3.0, 4.0, 5.0, 2.0]], "expected": [2.0, 2.0]}, "observation": {"pass": false, "actual": [2.0, 2.0], "expected": [2.0, 2.0]}}, {"input": {"args": [[5.5, 1.1, 3.3, 2.2]], "expected": [1.1, 2.2]}, "observation": {"pass": false, "actual": [2.2, 3.3], "expected": [1.1, 2.2]}}, {"input": {"args": [[10.0, 10.1, 10.2, 10.3]], "expected": [10.0, 10.1]}, "observation": {"pass": false, "actual": [10.0, 10.1], "expected": [10.0, 10.1]}}, {"input": {"args": [[-1.0, -2.0, -3.0, -4.0]], "expected": [-4.0, -3.0]}, "observation": {"pass": false, "actual": [-2.0, -1.0], "expected": [-4.0, -3.0]}}, {"input": {"args": [[0.0, 0.0, 1.0]], "expected": [0.0, 0.0]}, "observation": {"pass": false, "actual": [0.0, 0.0], "expected": [0.0, 0.0]}}]`
- HumanEval/20, adaptive: `[{"input": {"args": [[1.0, 2.0, 3.0, 4.0, 5.0, 2.2]], "expected": [2.0, 2.2]}, "observation": {"pass": false, "actual": [2.0, 2.2], "expected": [2.0, 2.2]}}, {"input": {"args": [[1.0, 2.0, 3.0, 4.0, 5.0, 2.0]], "expected": [2.0, 2.0]}, "observation": {"pass": false, "actual": [2.0, 2.0], "expected": [2.0, 2.0]}}, {"input": {"args": [[5.5, 1.1, 3.3, 2.2]], "expected": [1.1, 2.2]}, "observation": {"pass": false, "actual": [2.2, 3.3], "expected": [1.1, 2.2]}}, {"input": {"args": [[10.0, 10.1, 10.2, 10.3]], "expected": [10.0, 10.1]}, "observation": {"pass": false, "actual": [10.0, 10.1], "expected": [10.0, 10.1]}}, {"input": {"args": [[-1.0, -2.0, -3.0, -4.0]], "expected": [-4.0, -3.0]}, "observation": {"pass": false, "actual": [-2.0, -1.0], "expected": [-4.0, -3.0]}}, {"input": {"args": [[0.0, 0.0, 1.0]], "expected": [0.0, 0.0]}, "observation": {"pass": false, "actual": [0.0, 0.0], "expected": [0.0, 0.0]}}, {"input": {"args": [[5.5, 1.1, 3.3, 2.2]], "expected": [1.1, 2.2]}, "observation": {"pass": false, "actual": [2.2, 3.3], "expected": [1.1, 2.2]}}, {"input": {"args": [[10.0, 10.1, 10.2, 10.3]], "expected": [10.0, 10.1]}, "observation": {"pass": false, "actual": [10.0, 10.1], "expected": [10.0, 10.1]}}, {"input": {"args": [[-1.0, -2.0, -3.0, -4.0]], "expected": [-4.0, -3.0]}, "observation": {"pass": false, "actual": [-2.0, -1.0], "expected": [-4.0, -3.0]}}, {"input": {"args": [[0.0, 0.0, 1.0]], "expected": [0.0, 0.0]}, "observation": {"pass": false, "actual": [0.0, 0.0], "expected": [0.0, 0.0]}}, {"input": {"args": [[1.5, 1.6, 2.0, 2.1]], "expected": [1.5, 1.6]}, "observation": {"pass": false, "actual": [1.5, 1.6], "expected": [1.5, 1.6]}}, {"input": {"args": [[7.0, 3.0, 9.0, 5.0]], "expected": [3.0, 5.0]}, "observation": {"pass": false, "actual": [7.0, 9.0], "expected": [3.0, 5.0]}}]`
- HumanEval/21, fixed: `[{"input": {"args": [[5.0, 1.0, 3.0, 2.0, 4.0]], "expected": [1.0, 0.0, 0.6, 0.25, 0.8]}, "observation": {"pass": false, "actual": [1.0, 0.0, 0.5, 0.25, 0.75], "expected": [1.0, 0.0, 0.6, 0.25, 0.8]}}, {"input": {"args": [[-5.0, -2.0, 1.0, 4.0]], "expected": [0.0, 0.25, 0.5, 1.0]}, "observation": {"pass": false, "actual": [0.0, 0.3333333333333333, 0.6666666666666666, 1.0], "expected": [0.0, 0.25, 0.5, 1.0]}}, {"input": {"args": [[3.5, 3.5, 3.5, 3.5]], "expected": [0.0, 0.0, 0.0, 0.0]}, "observation": {"pass": false, "exception": "ZeroDivisionError"}}, {"input": {"args": [[5.0, 1.0, 3.0, 2.0, 4.0]], "expected": [1.0, 0.0, 0.6, 0.25, 0.8]}, "observation": {"pass": false, "actual": [1.0, 0.0, 0.5, 0.25, 0.75], "expected": [1.0, 0.0, 0.6, 0.25, 0.8]}}, {"input": {"args": [[-5.0, -2.0, 1.0, 4.0]], "expected": [0.0, 0.25, 0.5, 1.0]}, "observation": {"pass": false, "actual": [0.0, 0.3333333333333333, 0.6666666666666666, 1.0], "expected": [0.0, 0.25, 0.5, 1.0]}}, {"input": {"args": [[3.5, 3.5, 3.5, 3.5]], "expected": [0.0, 0.0, 0.0, 0.0]}, "observation": {"pass": false, "exception": "ZeroDivisionError"}}]`
- HumanEval/21, adaptive: `[{"input": {"args": [[5.0, 1.0, 3.0, 2.0, 4.0]], "expected": [1.0, 0.0, 0.6, 0.25, 0.8]}, "observation": {"pass": false, "actual": [1.0, 0.0, 0.5, 0.25, 0.75], "expected": [1.0, 0.0, 0.6, 0.25, 0.8]}}, {"input": {"args": [[-5.0, -2.0, 1.0, 4.0]], "expected": [0.0, 0.25, 0.5, 1.0]}, "observation": {"pass": false, "actual": [0.0, 0.3333333333333333, 0.6666666666666666, 1.0], "expected": [0.0, 0.25, 0.5, 1.0]}}, {"input": {"args": [[3.5, 3.5, 3.5, 3.5]], "expected": [0.0, 0.0, 0.0, 0.0]}, "observation": {"pass": false, "exception": "ZeroDivisionError"}}, {"input": {"args": [[3.5, 3.5, 3.5, 3.5]], "expected": [0.0, 0.0, 0.0, 0.0]}, "observation": {"pass": false, "exception": "ZeroDivisionError"}}, {"input": {"args": [[-5.0, -2.0, 1.0, 4.0]], "expected": [0.0, 0.25, 0.5, 1.0]}, "observation": {"pass": false, "actual": [0.0, 0.3333333333333333, 0.6666666666666666, 1.0], "expected": [0.0, 0.25, 0.5, 1.0]}}]`
- HumanEval/24, fixed: `[{"input": {"args": [1], "expected": 1}, "observation": {"pass": false, "exception": "ZeroDivisionError"}}]`
- HumanEval/24, adaptive: `[{"input": {"args": [1], "expected": 1}, "observation": {"pass": false, "exception": "ZeroDivisionError"}}]`
- HumanEval/26, adaptive: `[{"input": {"args": [], "expected": []}, "observation": {"pass": false, "exception": "TypeError"}}, {"input": {"args": [], "expected": []}, "observation": {"pass": false, "exception": "TypeError"}}]`

## Cost accounting

All project API requests so far: 124. List-price usage estimate: 0.146563 CNY. Conservative reservations: 0.827038 CNY.
Includes connectivity checks and the earlier execution pilot. Account billing may differ; this is not an invoice.
Internal reservation ceiling: 15 CNY, below the user-authorized 18 CNY. Requests are serialized, have no retries, and retain reservations on errors.

## Reproduction

Dependencies are locked in `uv.lock`. Input data is pinned to HumanEval commit `6d43fb980f9fee3c892a914eda09951f772ad10d`; Docker image digest is recorded in JSON.
Run `uv run python scripts/summarize.py` to regenerate this report without paid calls.
Run `uv run python scripts/compare.py` only for a new explicitly budgeted run; it refuses to overwrite the existing artifact.
