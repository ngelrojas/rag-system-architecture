# Chapter 5 — Orchestration and agentic RAG

**Book:** Part V · **Branch:** `feature/chapter-5` · **Builds on:** `feature/chapter-4`

| Commit | Section | What changes |
|---|---|---|
| 1 | 5.2 | `examples/idiomatic_langgraph.py` — the tutorial version, for contrast |
| 2 | 5.3 | `answer_graph.py` — LangGraph as a driving adapter around `AnswerQuestionHandler` |
| 3 | 5.4 | `ingest_review_graph.py`, `app/adapters/api/` — human-in-the-loop review over HTTP |
| 4 | 5.5 | `StructuredQueryPort`, `StructuredQueryHandler`, `multi_agent_graph.py`, `POST /route` |

## HTTP endpoints after this chapter

| Endpoint | Goes through |
|---|---|
| `POST /query` | `AnswerQuestionHandler` directly |
| `POST /ask` | the corrective answer graph (5.3) |
| `POST /route` | the multi-agent graph: documents, database, or both (5.5) |
| `POST /ingest` | `IngestDocumentHandler` directly |
| `POST /ingest/{doc_id}/submit` · `/approve` · `/reject` | the review graph (5.4) |

## Run it

```bash
make check
docker compose up -d && cp .env.example .env   # add OPENAI_API_KEY
uv run uvicorn main:api --reload               # http://localhost:8000/docs
```

Set `CHECKPOINT_DATABASE_URL=postgresql://rag:rag@localhost:5432/rag` to make review pauses survive a restart.

## Notes for readers of the book

- **5.3 — the retry loop needs a stopping rule.** As printed, a question with no relevant chunks loops until LangGraph's recursion limit fails the request. `build_answer_graph` takes `max_attempts` (default 2), and when an `LLMPort` is injected it reformulates the question before retrying, so the retry is actually corrective.
- **5.4 — the review flow.** As printed, `route_after_review` returns `"wait"` back to `review` while the status is pending, so the graph loops instead of reaching the `interrupt_before=["ingest"]` pause. Here `review → ingest` is a plain edge, the interrupt pauses before `ingest`, and `ingest_node` only writes when the status is `approved`. There is also a `/reject` endpoint.
- **5.5 — `StructuredQueryPort`** is introduced here (the book first names it in 6.3), with SQLite and Postgres adapters.
- `app/application.py` holds the shape of the wired application so the HTTP adapter can use it without importing the composition root — contract 6 enforces that.
