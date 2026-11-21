# Chapter 7 — The complete reference system

**Book:** Part VII · **Branch:** `feature/chapter-7` (= `master`) · **Builds on:** `feature/chapter-6`

| Commit | Section | What changes |
|---|---|---|
| 1 | 7.1 | `DEPLOYMENT_MODE=offline`, `scripts/demo.py`, `tests/test_end_to_end.py`, sample documents |
| 2 | 7.2 | `docs/diagrams/` — the three diagrams as Mermaid, next to the code |
| 3 | 7.3–7.4 | These notes and the final README |

## See the whole system run — no key, no Docker

```bash
make install
make demo
```

The demo builds the application through the real composition root and exercises every driving path over HTTP: ingestion (command side), queries with evaluation checks and a trace id, the corrective answer graph, the multi-agent router hitting a SQLite catalog, the human-in-the-loop review, the per-request spans, and PII redaction.

## Run it for real

```bash
docker compose up -d
cp .env.example .env          # OPENAI_API_KEY, or DEPLOYMENT_MODE=sovereign with Ollama
make serve                    # http://localhost:8000/docs
```

## Where each Part lives

| Part | Look at |
|---|---|
| I — the model layer | `app/ports.py` (`LLMPort`), `app/adapters/openai_llm.py`, `app/adapters/local_llm.py` |
| II — the retrieval path | `app/core/chunking.py`, `EmbeddingPort`, `app/adapters/qdrant_store.py` |
| III — software architecture | `app/composition.py`, `app/core/`, `.importlinter`, `relay.py` |
| IV — CQRS | `app/core/commands.py`, `queries.py`, `ingest_handler.py`, `query_handler.py`, `RetrievalPort` |
| V — orchestration | `app/adapters/orchestration/`, `app/adapters/api/review_endpoints.py` |
| VI — cross-cutting concerns | `app/evaluation/`, `app/observability/`, `app/compliance/`, `app/core/query_budget.py` |
| VII — the reference | `docs/diagrams/`, `scripts/demo.py`, `tests/test_end_to_end.py` |

## The anti-patterns (7.4), and the gate that catches each one

| Anti-pattern | What stops it here |
|---|---|
| The rotting script | `naive/` is kept outside every contract; nothing in `app/` may look like it |
| Vendor calls in the domain | import-linter contracts 1 and 4, `tests/test_architecture_boundaries.py` |
| The framework as the architecture | contract 5: orchestration may not import concrete adapters |
| One model for reads and writes | `VectorStorePort` has no `search`; `RetrievalPort` has no writes |
| Cross-cutting code inside handlers | contract 8: wrappers wrap ports, and only the composition root applies them |
| Unbounded loops and costs | `max_attempts` in the answer graph, `QueryBudget` per request |
