# tests/test_cqrs_handlers.py — 4.2, commands and queries as a formal split
from app.core.commands import IngestDocumentCommand, IngestDocumentHandler
from app.core.queries import AnswerQuestionHandler, AnswerQuestionQuery
from app.testing.fakes import FakeEmbedder, FakeLLM, FakeVectorStore


def test_command_returns_only_a_confirmation() -> None:
    handler = IngestDocumentHandler(embedder=FakeEmbedder(), vector_store=FakeVectorStore(), chunk_size=100)
    result = handler.handle(IngestDocumentCommand(doc_id="doc-1", text="z" * 150))
    assert (result.doc_id, result.chunks_ingested, result.succeeded) == ("doc-1", 2, True)


def test_query_carries_its_own_relevance_policy() -> None:
    store = FakeVectorStore(results=[("relevant", 0.9), ("noise", 0.1)])
    handler = AnswerQuestionHandler(llm=FakeLLM(response="ok"), embedder=FakeEmbedder(), vector_store=store)
    result = handler.handle(AnswerQuestionQuery(question="q", min_relevance=0.5))
    assert result.chunks_used == ["relevant"]
