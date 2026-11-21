# tests/test_ingest_handler.py — 3.5
#
# The test this refactor was always in service of: structurally impossible
# to write cleanly against the Part II version, because there was no seam to
# substitute a failure into.
from app.core.ingest_handler import IngestHandler
from app.testing.fakes import FailingAfterNCallsVectorStore, FakeEmbedder, FakeVectorStore


def test_partial_ingestion_is_rolled_back() -> None:
    store = FailingAfterNCallsVectorStore(fail_after=2)
    handler = IngestHandler(embedder=FakeEmbedder(), vector_store=store, chunk_size=100)

    result = handler.handle(doc_id="doc-42", text="a" * 500)  # yields 5 chunks

    assert result.succeeded is False
    assert result.chunks_ingested == 0
    assert store.delete_prefix_called_with == "doc-42"
    assert store.rows == {}  # nothing half-ingested survives


def test_successful_ingestion_reports_every_chunk() -> None:
    store = FakeVectorStore()
    handler = IngestHandler(embedder=FakeEmbedder(), vector_store=store, chunk_size=100)

    result = handler.handle(doc_id="doc-7", text="b" * 250)

    assert result.succeeded is True
    assert result.chunks_ingested == 3
    assert sorted(store.rows) == ["doc-7-0", "doc-7-1", "doc-7-2"]
