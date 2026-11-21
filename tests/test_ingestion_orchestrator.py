# tests/test_ingestion_orchestrator.py — 2.4
from services.ingestion import ChunkStatus, IngestionOrchestrator
from tests.fakes import FakeEmbedder, FakeVectorStore


def test_every_chunk_gets_an_outcome() -> None:
    store = FakeVectorStore()
    orchestrator = IngestionOrchestrator(embedder=FakeEmbedder(fail_on_call=3), store=store)

    outcomes = orchestrator.ingest("policy", ["a", "b", "c", "d"])

    assert [o.status for o in outcomes] == [
        ChunkStatus.STORED,
        ChunkStatus.STORED,
        ChunkStatus.FAILED,
        ChunkStatus.STORED,
    ]
    assert outcomes[2].error == "embedding provider timed out"
    # The failure is now visible and owned — but the document is still partly
    # stored. Deciding what to do about that is Part III's job (3.5).
    assert set(store.rows) == {"policy-0", "policy-1", "policy-3"}
