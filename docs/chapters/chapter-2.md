# Chapter 2 — The retrieval path

**Book:** Part II · **Branch:** `feature/chapter-2` · **Builds on:** `feature/chapter-1`

| Commit | Section | What changes |
|---|---|---|
| 1 | 2.1 | `naive/ingest.py`, `naive/query.py` — the naive pipeline, runnable with an OpenAI key |
| 2 | 2.2 | `domain/chunking.py` — the chunking decision gets an owner |
| 3 | 2.3 | `tests/test_naive_partial_failure.py` — the half-ingested document, documented |
| 4 | 2.4 | `EmbeddingPort`, `VectorStorePort`, `IngestionOrchestrator`, `RetrievalOrchestrator`, OpenAI and Qdrant adapters |

## Layout after this chapter

```
domain/
  ports.py          LLMPort, EmbeddingPort, VectorStorePort, Match
  chunking.py       split_into_chunks(text, chunk_size)
  answering.py
services/
  ingestion.py      IngestionOrchestrator — every chunk gets an outcome
  retrieval.py      RetrievalOrchestrator
adapters/
  openai_llm.py  openai_embeddings.py  qdrant_store.py
naive/              the 2.1 pipeline, kept for comparison
```

## Run it

```bash
make check                              # no keys, no Docker: fakes + in-process Qdrant
docker compose up -d                    # a real Qdrant on :6333
uv run python -m naive.run_pipeline     # the naive pipeline (needs OPENAI_API_KEY)
```

Notice what `tests/test_ingestion_orchestrator.py` proves — and what it doesn't. The failure is now *visible*, but the document is still partly stored. Who decides what that means? That question is where Part III starts.
