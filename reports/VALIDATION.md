# Validation — 2026-10-01

Latest local suite: **26 passed in 1.18s**. CI workflow provided for a standalone repository; remote CI has not been run.

- Live Qwen3-Coder-Flash API: connectivity, test generation and budgeted LangChain/LangGraph flow exercised.
- Docker: pinned Python image, no network, read-only filesystem, unprivileged user, resource limits;
  behavioral candidate tests executed successfully.
- ReAct live sequence: test → retrieve → syntax → test; SQLite checkpoint state persisted.
- Development: 15 seed tasks → 8 qualified pairs → 16 candidates; exclusions retained.
- Task-disjoint transfer: 15 seed tasks → 6 qualified pairs → 12 candidates; exclusions retained.
- Adaptive automatic rejection did not pass the promotion gate. Product now requires review for
  model-generated test failures; recorded experiments have not been rewritten.
- FastAPI: allowlisted read-only reports, health endpoint, costs; desktop dashboard inspected in browser.
- Costs: `api-ledger.jsonl` records reservations, returned usage and list-price estimates, not billing receipts.

Remaining limitations: non-adversarial function-level tasks, one model/one run per condition,
public-data contamination possible, no repository-disjoint benchmark, no RAG ablation, no RSI evidence,
no unified-diff application, no hostile-candidate output integrity guarantee.
