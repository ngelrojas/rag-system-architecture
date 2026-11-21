# app/composition.py — the composition root (3.4, reshaped for CQRS in 4.4)
#
# This is the ONLY file in the application allowed to import
# concrete adapters. Every other module imports ports.
from dataclasses import dataclass

from app.adapters.openai_embeddings import OpenAIEmbeddings
from app.adapters.openai_llm import OpenAILLM
from app.adapters.qdrant_store import QdrantRetriever, QdrantVectorStore
from app.config import Settings
from app.core.ingest_handler import IngestDocumentHandler
from app.core.query_handler import AnswerQuestionHandler
from app.ports import EmbeddingPort, LLMPort, RetrievalPort, VectorStorePort


@dataclass
class Application:
    """Everything the API layer needs, fully wired."""

    query_handler: AnswerQuestionHandler
    ingest_handler: IngestDocumentHandler


def build_application(settings: Settings) -> Application:
    embedder: EmbeddingPort = OpenAIEmbeddings(api_key=settings.openai_api_key, model=settings.embedding_model)
    llm: LLMPort = OpenAILLM(
        api_key=settings.openai_api_key, model=settings.llm_model, timeout_s=settings.llm_timeout_s
    )

    # Command side: strict, immediately-consistent writes.
    vector_store: VectorStorePort = QdrantVectorStore(url=settings.qdrant_url, collection=settings.qdrant_collection)

    # Query side: can point at the *same* store today...
    retriever: RetrievalPort = QdrantRetriever(url=settings.qdrant_url, collection=settings.qdrant_collection)
    # ...or, later, without touching AnswerQuestionHandler at all, a
    # read replica or a caching layer:
    #
    # retriever: RetrievalPort = CachedRetriever(
    #     inner=QdrantRetriever(url=settings.qdrant_read_replica_url, ...),
    #     ttl_s=30,
    # )

    ingest_handler = IngestDocumentHandler(embedder=embedder, vector_store=vector_store, chunk_size=settings.chunk_size)
    query_handler = AnswerQuestionHandler(llm=llm, embedder=embedder, retriever=retriever)

    return Application(query_handler=query_handler, ingest_handler=ingest_handler)
