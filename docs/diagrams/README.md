# Architecture diagrams (7.2)

Diagrams as code: each `.mmd` file lives in the repository next to the code it describes, so it is reviewed, diffed and updated with that code. GitHub renders the blocks below.

## Diagram 1 — Package structure (class diagram)

Source: [`01-package-structure.mmd`](01-package-structure.mmd) · Maps to: `app/ports.py`, `app/core/`, `app/adapters/`. Notice what has no arrow: `AnswerQuestionHandler` and `IngestDocumentHandler` share nothing but `EmbeddingPort` — that absence is Part IV.

```mermaid
classDiagram
    direction TB
    class AnswerQuestionHandler {
        -LLMPort llm
        -EmbeddingPort embedder
        -RetrievalPort retriever
        +handle(AnswerQuestionQuery) AnsweredQuestion
    }
    class IngestDocumentHandler {
        -EmbeddingPort embedder
        -VectorStorePort vector_store
        -int chunk_size
        +handle(IngestDocumentCommand) IngestResult
    }
    class RetrievalPort {
        <<interface>>
        +search(embedding, top_k) list~RetrievedChunk~
    }
    class LLMPort {
        <<interface>>
        +complete(prompt) str
    }
    class EmbeddingPort {
        <<interface>>
        +embed(text) list~float~
    }
    class VectorStorePort {
        <<interface>>
        +upsert(key, embedding, metadata)
        +delete_prefix(prefix)
    }
    AnswerQuestionHandler --> RetrievalPort
    AnswerQuestionHandler --> LLMPort
    AnswerQuestionHandler --> EmbeddingPort
    IngestDocumentHandler --> EmbeddingPort
    IngestDocumentHandler --> VectorStorePort
    QdrantRetriever ..|> RetrievalPort
    OpenAILLM ..|> LLMPort
    LocalLLM ..|> LLMPort
    OpenAIEmbeddings ..|> EmbeddingPort
    LocalEmbeddings ..|> EmbeddingPort
    QdrantVectorStore ..|> VectorStorePort
```

## Diagram 2 — Request lifecycle (sequence diagram)

Source: [`02-request-lifecycle.mmd`](02-request-lifecycle.mmd) · Maps to: `app/adapters/api/http_handler.py` → `app/adapters/orchestration/` → `app/core/query_handler.py`.

```mermaid
sequenceDiagram
    participant API as API adapter
    participant Router as Routing graph (5.5)
    participant AQH as AnswerQuestionHandler
    participant Ret as RetrievalPort (guarded)
    participant LLM as LLMPort (traced, budgeted)
    API->>Router: question
    Router->>Router: classify
    Router->>AQH: dispatch (semantic)
    AQH->>Ret: search(embedding, top_k)
    Ret-->>AQH: candidates
    AQH->>AQH: filter by relevance (3.3)
    AQH->>LLM: complete(prompt)
    LLM-->>AQH: answer
    AQH-->>Router: AnsweredQuestion
    Router-->>API: final response
```

## Diagram 3 — Ingestion state machine

Source: [`03-ingestion-states.mmd`](03-ingestion-states.mmd) · Maps to: `app/core/ingest_handler.py`: there is no path from `Ingesting` to the end state that skips both `Committed` and `Failed`.

```mermaid
stateDiagram-v2
    [*] --> Ingesting
    Ingesting --> ChunkEmbedded: embed + upsert each chunk
    ChunkEmbedded --> Ingesting: more chunks remain
    ChunkEmbedded --> Committed: all chunks written
    Ingesting --> RollingBack: any chunk fails
    RollingBack --> Failed: delete_prefix complete
    Committed --> [*]
    Failed --> [*]
```
