# app/composition.py — the composition root (3.4, CQRS in 4.4, graphs in Part V)
#
# This is the ONLY file in the application allowed to import
# concrete adapters. Every other module imports ports.
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver

from app.adapters.openai_embeddings import OpenAIEmbeddings
from app.adapters.openai_llm import OpenAILLM
from app.adapters.orchestration.answer_graph import build_answer_graph
from app.adapters.orchestration.ingest_review_graph import build_ingest_review_graph
from app.adapters.orchestration.multi_agent_graph import build_multi_agent_graph
from app.adapters.postgres_structured_query import PostgresStructuredQuery
from app.adapters.qdrant_store import QdrantRetriever, QdrantVectorStore
from app.adapters.sqlite_structured_query import SqliteStructuredQuery
from app.application import Application
from app.config import Settings
from app.core.ingest_handler import IngestDocumentHandler
from app.core.query_handler import AnswerQuestionHandler
from app.core.structured_query_handler import StructuredQueryHandler
from app.ports import EmbeddingPort, LLMPort, RetrievalPort, StructuredQueryPort, VectorStorePort


def build_checkpointer(settings: Settings) -> BaseCheckpointSaver:
    """Durable pauses need a durable checkpointer (5.4). Without a database
    URL the review graph still works, but pauses only live as long as the process."""
    if not settings.checkpoint_database_url:
        return InMemorySaver()
    import psycopg
    from langgraph.checkpoint.postgres import PostgresSaver
    from psycopg.rows import dict_row

    conn = psycopg.connect(settings.checkpoint_database_url, autocommit=True, prepare_threshold=0, row_factory=dict_row)
    saver = PostgresSaver(conn)
    saver.setup()
    return saver


def build_structured_port(settings: Settings) -> StructuredQueryPort:
    url = settings.structured_database_url
    if url.startswith("sqlite:///"):
        return SqliteStructuredQuery(path=url.removeprefix("sqlite:///"))
    return PostgresStructuredQuery(connection_string=url)


def wire(
    settings: Settings,
    llm: LLMPort,
    embedder: EmbeddingPort,
    vector_store: VectorStorePort,
    retriever: RetrievalPort,
    structured_db: StructuredQueryPort,
    checkpointer: BaseCheckpointSaver,
) -> Application:
    """Build handlers and graphs from already-chosen ports. Tests and the
    offline demo call this directly with fakes."""
    ingest_handler = IngestDocumentHandler(embedder=embedder, vector_store=vector_store, chunk_size=settings.chunk_size)
    query_handler = AnswerQuestionHandler(llm=llm, embedder=embedder, retriever=retriever)
    structured_handler = StructuredQueryHandler(llm=llm, db=structured_db, schema=settings.nlq_schema)
    min_relevance = settings.min_relevance_threshold
    return Application(
        query_handler=query_handler,
        ingest_handler=ingest_handler,
        structured_handler=structured_handler,
        answer_graph=build_answer_graph(query_handler, llm=llm, min_relevance=min_relevance),
        review_graph=build_ingest_review_graph(ingest_handler, checkpointer),
        multi_agent_graph=build_multi_agent_graph(query_handler, structured_handler, llm, min_relevance=min_relevance),
        min_relevance=min_relevance,
        judge_llm=llm,
        judge_sample_rate=settings.judge_sample_rate,
    )


def build_application(settings: Settings) -> Application:
    embedder: EmbeddingPort = OpenAIEmbeddings(api_key=settings.openai_api_key, model=settings.embedding_model)
    llm: LLMPort = OpenAILLM(
        api_key=settings.openai_api_key, model=settings.llm_model, timeout_s=settings.llm_timeout_s
    )
    # Command side and query side resolved independently (4.3).
    vector_store: VectorStorePort = QdrantVectorStore(url=settings.qdrant_url, collection=settings.qdrant_collection)
    retriever: RetrievalPort = QdrantRetriever(url=settings.qdrant_url, collection=settings.qdrant_collection)

    return wire(
        settings, llm, embedder, vector_store, retriever, build_structured_port(settings), build_checkpointer(settings)
    )
