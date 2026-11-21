# app/composition.py — the composition root (3.4)
#
# This is the ONLY file in the application allowed to import
# concrete adapters. Every other module imports ports.
from dataclasses import dataclass

from app.adapters.openai_embeddings import OpenAIEmbeddings
from app.adapters.openai_llm import OpenAILLM
from app.adapters.qdrant_store import QdrantVectorStore
from app.config import Settings
from app.core.ingest_handler import IngestHandler
from app.core.query_handler import QueryHandler
from app.ports import EmbeddingPort, LLMPort, VectorStorePort


@dataclass
class Application:
    """Everything the API layer needs, fully wired."""

    query_handler: QueryHandler
    ingest_handler: IngestHandler


def build_application(settings: Settings) -> Application:
    """
    The composition root. Construction happens here, once,
    at startup — never inside a handler, never inside the core.
    """
    llm: LLMPort = OpenAILLM(
        api_key=settings.openai_api_key,
        model=settings.llm_model,
        timeout_s=settings.llm_timeout_s,
    )
    embedder: EmbeddingPort = OpenAIEmbeddings(
        api_key=settings.openai_api_key,
        model=settings.embedding_model,
    )
    vector_store: VectorStorePort = QdrantVectorStore(
        url=settings.qdrant_url,
        collection=settings.qdrant_collection,
    )

    query_handler = QueryHandler(
        llm=llm,
        embedder=embedder,
        vector_store=vector_store,
        min_relevance=settings.min_relevance_threshold,
    )
    ingest_handler = IngestHandler(
        embedder=embedder,
        vector_store=vector_store,
        chunk_size=settings.chunk_size,
    )

    return Application(
        query_handler=query_handler,
        ingest_handler=ingest_handler,
    )
