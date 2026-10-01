# API setup and budget

The local `.env` is ignored by Git and has mode 0600. Never include it in a release archive.
Only public experimental inputs may be sent to the configured provider.

```sh
uv run patchscope review --repo data/graph-smoke/repo --candidate data/graph-smoke/candidate.py \
  --task 'Inspect has_close_elements against its contract' --api-env .env \
  --ledger reports/api-ledger.jsonl --output reports/live-graph.json
```

The budgeted path uses a LangChain runnable/parser pipeline, LangGraph orchestration, and
an OpenAI-compatible HTTP client that reserves estimated worst-case call cost before sending.
The model is `qwen3-coder-flash`, selected from the authenticated `/models` response.
Base URL and API key are read only from the local configuration; credentials are not logged.

Budget approved 2026-10-01: **18 CNY**. Application reservation ceiling: **15 CNY**.
Price assumption: Beijing, <=32K input, 1 CNY/million input and 4 CNY/million output tokens.
Source: https://help.aliyun.com/zh/model-studio/qwen3-coder-flash

Requests are serialized under a file lock. Reservations are never released, even for failed calls;
this intentionally overcounts. No automatic retries. Actual usage is saved separately when returned.
The ledger is not a billing API: list-price calculations do not prove the account's charged amount.
No external tracing service is configured by this project.

The original optional `--model` provider path is a generic integration and does not use this ledger.
All experiments for this authorized budget must use `BudgetClient` / `--api-env`.
