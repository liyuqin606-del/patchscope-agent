# Frozen transfer run — 2026-10-01

Before invoking the transfer script:

- Data: HumanEval indices 15–29 inclusive, disjoint from development indices 0–14.
- Same one-mutation rule and qualification; no replacement of excluded tasks.
- Conditions: fixed and feedback-adaptive, two requests each, 1200 output-token ceiling.
- Same prompts, model, tool permissions, candidate access and execution rules.
- Parser v2 accepts a single full-response Markdown JSON fence, then applies the same schema.
  Truncation, prose around JSON and malformed cases remain errors. Both conditions use v2.
- Keep original development results unchanged. Development/transfer are not directly identical
  configurations due to parser repair; compare conditions within each run.
- No prompt tuning or selection on transfer results. This is task transfer inside a single public
  benchmark, **not** repository transfer or protection from model training contamination.
- The adaptive policy was motivated by development results; report its false rejections and costs
  even if transfer is unfavorable. The experiment does not evaluate RAG or RSI gains.
