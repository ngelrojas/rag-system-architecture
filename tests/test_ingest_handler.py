# tests/test_ingest_handler.py — 3.5's policy on the command side (4.4)
from app.core.commands import IngestDocumentCommand
from app.core.ingest_handler import IngestDocumentHandler
from app.testing.fakes import FailingAfterNCallsVectorStore, FakeEmbedder, FakeVectorStore


def test_partial_ingestion_is_rolled_back() -> None:
    store = FailingAfterNCallsVectorStore(fail_after=2)
    handler = IngestDocumentHandler(embedder=FakeEmbedder(), vector_store=store, chunk_size=100)

    result = handler.handle(IngestDocumentCommand(doc_id="doc-42", text="a" * 500))  # yields 5 chunks

    assert result.succeeded is False
    assert result.chunks_ingested == 0
    assert store.delete_prefix_called_with == "doc-42"
    assert store.rows == {}


def test_command_returns_only_a_confirmation() -> None:
    store = FakeVectorStore()
    handler = IngestDocumentHandler(embedder=FakeEmbedder(), vector_store=store, chunk_size=100)

    result = handler.handle(IngestDocumentCommand(doc_id="doc-7", text="b" * 250))

    assert (result.doc_id, result.chunks_ingested, result.succeeded) == ("doc-7", 3, True)
    assert sorted(store.rows) == ["doc-7-0", "doc-7-1", "doc-7-2"]
