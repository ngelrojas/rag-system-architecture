# Chapter 3 — Software architecture: the hexagon

**Book:** Part III · **Branch:** `feature/chapter-3` · **Builds on:** `feature/chapter-2`

| Commit | Section | What changes |
|---|---|---|
| 1 | 3.2–3.3 | Everything moves into `app/`: ports at the edge, policy in `app/core`, vendors in `app/adapters` |
| 2 | 3.5 | `IngestHandler` — the rollback policy: a document is fully retrievable or not at all |
| 3 | 3.4 | `Settings`, `QueryHandler` (3.3's policies), `app/composition.py`, `main.py` (FastAPI) |
| 4 | 3.6 | Three import-linter contracts and an `ast` boundary test |
| 5 | 3.8 | `PostgresVectorStoreWithOutbox`, `relay.py`, `sql/001_outbox.sql`, Postgres in docker compose |

> 3.5 is committed before 3.4 because the composition root wires `IngestHandler`, so the handler has to exist first. Read them in the book's order; the code is the same.

## Layout after this chapter

```
app/
  ports.py                LLMPort, EmbeddingPort, VectorStorePort, RetrievedChunk
  config.py               Settings (env vars / .env)
  composition.py          the composition root — the only module that imports adapters
  core/
    chunking.py           split_into_chunks
    query_handler.py      QueryHandler — relevance threshold, refuse when nothing is relevant
    ingest_handler.py     IngestHandler — all-or-nothing ingestion
  adapters/
    openai_llm.py  openai_embeddings.py  qdrant_store.py  postgres_outbox_store.py
  testing/fakes.py        FakeLLM, FakeEmbedder, FakeVectorStore, FailingAfterNCallsVectorStore
main.py                   FastAPI: POST /query, POST /ingest
relay.py                  the outbox relay process
sql/001_outbox.sql
```

## Run it

```bash
make check                       # all gates, no keys needed
docker compose up -d             # Qdrant :6333 and Postgres :5432
cp .env.example .env             # add OPENAI_API_KEY
uv run uvicorn main:api --reload # http://localhost:8000/docs
uv run python relay.py           # the outbox relay
```

## Notes for readers of the book

- In the book's 3.5 listing `VectorStorePort` has only `upsert` and `delete_prefix`, but `QueryHandler` (3.4) also needs to search. Here `VectorStorePort` keeps a `search` method for Part III; 4.3 moves it to its own `RetrievalPort`.
- 3.7 (modular monolith vs microservices) is a decision, not code. Its `IngestServiceClient` sketch appears in chapter 4, because it uses Part IV's command types.
- 3.8: `chunks` writes use `ON CONFLICT … DO UPDATE` so re-ingesting is idempotent, and the relay orders events by `created_at` (a UUID `id` has no order).
