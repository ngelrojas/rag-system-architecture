# Chapter 4 — CQRS

**Book:** Part IV (and the 3.7 sketch) · **Branch:** `feature/chapter-4` · **Builds on:** `feature/chapter-3`

| Commit | Section | What changes |
|---|---|---|
| 1 | 4.1 | `DocumentService` — clean ports, one shared model; its tests show the cost |
| 2 | 4.2 | `commands.py` / `queries.py` — each side owns its own model and handler |
| 3 | 4.3–4.4 | `RetrievalPort`, `QdrantRetriever`, `CachedRetriever`; handlers move to `ingest_handler.py` / `query_handler.py`; `DocumentService` disappears |
| 4 | 3.7 | `IngestServiceClient` — the same command, forwarded to a separate service |

Compare the branch tip with Part III:

```bash
git diff feature/chapter-3 feature/chapter-4 -- app/
```

## Layout after this chapter

```
app/
  ports.py                 LLMPort, EmbeddingPort, VectorStorePort (write), RetrievalPort (read), RetrievedChunk
  core/
    commands.py            IngestDocumentCommand, IngestResult
    queries.py             AnswerQuestionQuery, AnsweredQuestion
    ingest_handler.py      IngestDocumentHandler
    query_handler.py       AnswerQuestionHandler — depends on RetrievalPort
  adapters/
    qdrant_store.py        QdrantVectorStore (write) + QdrantRetriever (read)
    cached_retriever.py    CachedRetriever — wraps any RetrievalPort
    ingest_service_client.py
```

## Notes for readers of the book

- 4.2 defines the handlers inside `commands.py` and `queries.py`; 4.4 moves them to `ingest_handler.py` and `query_handler.py`. The commits follow that order, so both versions are in the history.
- `AnswerQuestionHandler` keeps 3.3's grounding policy: when no candidate clears `min_relevance`, it returns a refusal without calling the LLM.
- `QdrantVectorStore` and `QdrantRetriever` accept an optional shared `QdrantClient`, so tests and demos can run both sides against one in-process Qdrant.
