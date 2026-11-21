# tests/test_retrieval_orchestrator.py — 2.4
from domain.ports import Match
from services.retrieval import RetrievalOrchestrator
from tests.fakes import FakeEmbedder, FakeVectorStore


def test_retrieve_returns_chunk_texts_in_rank_order() -> None:
    store = FakeVectorStore(
        matches=[Match("d-0", 0.9, {"text": "first"}), Match("d-1", 0.7, {"text": "second"})]
    )
    retriever = RetrievalOrchestrator(embedder=FakeEmbedder(), store=store)
    assert retriever.retrieve("question", top_k=2) == ["first", "second"]
