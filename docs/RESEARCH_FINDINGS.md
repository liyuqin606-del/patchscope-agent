# What the first real experiments changed

The development experiment initially favored feedback-adaptive test generation on detection:
8/8 wrong candidates detected, versus 6/8 for fixed generation, with 2/8 correct candidates falsely
rejected in either condition. Fifteen seed tasks produced eight qualifying task pairs; seven exclusions
were retained. This was a pilot, not evidence of broad superiority.

A frozen transfer run used the next fifteen public tasks. Six task pairs qualified; nine exclusions
were retained. Both conditions detected 6/6 wrong candidates, while fixed falsely rejected 3/6 correct
candidates and adaptive falsely rejected 4/6. Parser v2 was applied symmetrically within transfer.
The adaptive advantage did not transfer. Generated expectations and input validity need stronger checks.

## Resulting engineering decision

- No promotion of adaptive automatic rejection (`reports/harness-decision.json`).
- A generated-test failure now yields `review_required` with the exact evidence.
- Syntax-invalid complete Python files can still be rejected by the deterministic syntax checker.
- Passing checks yield `insufficient_evidence`, never automatic acceptance.
- Original experimental verdicts remain unchanged, including errors and false rejections.
- The existing live trace was replayed through the new adjudicator without API calls;
  `reports/advisory-replay.json` records the old and current decisions.

This change prevents an unverified generated expectation from directly rejecting a patch. It does
not improve the measured accuracy of the test generator, and we do not relabel benchmark failures
as successes. It changes the product's automation boundary in response to observed failure.

## What can go on a CV

- Implemented a LangGraph/ReAct verification workflow integrating LangChain structured actions,
  hybrid code retrieval, SQLite checkpoints, isolated Docker execution and a FastAPI evidence viewer.
- Built a reproducible evaluation pipeline with pinned public inputs, matched call limits, separate
  scoring tests, preserved error/exclusion records, cost reservations and raw trace replay.
- Evaluated fixed and feedback-adaptive verification on 28 qualified candidates from 30 seed tasks;
  found a transfer failure and introduced an evidence-review gate instead of automatic rejection.

Do not claim RSI gains, repository-level generalization, reduced false-positive rates, or a significant
accuracy improvement. The current harness improvement code is bounded policy selection with a promotion
gate; recursive modification of the improver has not been implemented or validated.
