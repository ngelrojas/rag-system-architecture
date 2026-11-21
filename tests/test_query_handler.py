# tests/test_query_handler.py — 3.4
from app.core.query_handler import NO_GROUNDED_ANSWER, QueryHandler
from app.testing.fakes import FakeEmbedder, FakeLLM, FakeVectorStore


def test_query_handler_respects_relevance_threshold() -> None:
    fake_store = FakeVectorStore(results=[("chunk-a", 0.92), ("chunk-b", 0.31)])
    handler = QueryHandler(
        llm=FakeLLM(response="answer grounded in chunk-a"),
        embedder=FakeEmbedder(),
        vector_store=fake_store,
        min_relevance=0.5,
    )

    result = handler.handle("what does the policy say about X?")

    # chunk-b (0.31) is below threshold and must not reach the LLM
    assert "chunk-b" not in result.chunks_used
    assert "chunk-a" in result.chunks_used


def test_nothing_relevant_means_no_llm_call() -> None:
    llm = FakeLLM()
    handler = QueryHandler(
        llm=llm,
        embedder=FakeEmbedder(),
        vector_store=FakeVectorStore(results=[("weak", 0.2)]),
        min_relevance=0.5,
    )

    result = handler.handle("anything")

    assert result.answer == NO_GROUNDED_ANSWER
    assert llm.prompts == []  # the grounding policy refused before the model was asked
