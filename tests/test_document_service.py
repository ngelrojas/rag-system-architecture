# tests/test_document_service.py — 4.1, what the shared model costs
#
# Testing query() alone still requires a fake that implements upsert and
# delete_prefix — mutation methods the query path never uses — and the
# test asserts nothing about them. 4.4's test needs none of that.
from app.core.document_service import DocumentService
from app.testing.fakes import FakeEmbedder, FakeLLM, FakeVectorStore


def test_query_needs_a_write_capable_fake() -> None:
    store = FakeVectorStore(results=[("relevant", 0.9), ("noise", 0.1)])
    service = DocumentService(llm=FakeLLM(response="ok"), embedder=FakeEmbedder(), vector_store=store)

    assert service.query("question") == "ok"
    # Note what the shared shape hides: "noise" (0.1) reached the prompt,
    # because no read-side model exists to hold a relevance policy.


def test_ingest_returns_the_whole_document_model() -> None:
    service = DocumentService(llm=FakeLLM(), embedder=FakeEmbedder(), vector_store=FakeVectorStore())
    document = service.ingest("doc-1", "x" * 1200)
    # The write path hands back embeddings and chunks nobody on the write side asked for.
    assert len(document.chunks) == 3 and len(document.embeddings) == 3
