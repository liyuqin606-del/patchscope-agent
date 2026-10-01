# Evaluation contract (draft before data collection)

Unit: one fixed candidate patch for one task. Keep the candidate unchanged across verifier conditions.
Ground-truth organizer tests are available only to the scorer, never retrieval or the proposer.
Split by repository; use development for selection and hold out final repositories once. Deduplicate
related patches before splitting. Report both correct and incorrect patch denominators.

Conditions: existing tests; static checks; scripted tool policy; ReAct without retrieval; ReAct with
retrieval; selected harness; equal-budget random policy search. Fix model/version, seed lists,
retrieval corpus and budgets. Count proposer selection costs as well as final verifier costs.

Metrics: wrong-patch detection; correct-patch false rejection; abstention; infrastructure errors;
wall time; model input/output tokens and monetary cost. A zero observed false-rejection count is
not proof of zero population risk. Report binomial intervals and paired uncertainty estimates;
with multiple patches per repository, bootstrap at repository level.

Promotion: no held-out labels in search; preserve baseline on ties or regression; save parent
policy, candidate configuration, dataset hashes and exact evaluation receipt. A deployed rollback
registry and held-out promotion runner are not implemented yet.

Current evidence: offline fixtures plus live public HumanEval mutation pilots. See RESEARCH_FINDINGS.md.
These are task-level pilots, not the repository-disjoint evaluation specified above.
