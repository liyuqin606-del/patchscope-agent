# Code reading guide

Read in this order:

1. `retrieval.py`: immutable source chunks → sparse retrieval → reciprocal rank fusion → citations.
2. `agent.py`: typed graph state → structured action → tools → observation → independent adjudicator.
3. `checks.py`: syntax-only evidence and the separate container execution boundary.
4. `evolution.py`: baseline → candidate policy metrics → constraints → fallback/selection receipt.
5. `tests/test_system.py`: counterexamples that define the evidence boundaries.

The ReAct planner chooses what to inspect, not what is true. `adjudicate` rejects syntax-invalid complete Python candidates, requires review for generated-test failures,
and otherwise abstains. This is intentionally conservative:
adding behavioral acceptance requires a validated execution protocol rather than a stronger prompt.

The word and character retrieval channels both operate on code text. They are lexical channels,
not an embedding model. This keeps the first version offline and reproducible. A dense channel must
be evaluated with retrieval ablations before it is described as an improvement.

The evolution code does not edit itself. It is an initial substrate for harness optimization:
policy definitions are explicit, development data is hashed, and regression returns the baseline.
Future recursive improvement must show the improver itself becomes better on new tasks.
