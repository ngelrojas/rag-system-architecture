# tests/test_answer_question_handler.py — 4.4
#
# No write-capable fake, no mutation methods to quietly ignore: the query
# side's test only needs what the query side uses.
from app.core.queries import AnswerQuestionQuery
from app.core.query_handler import NO_GROUNDED_ANSWER, AnswerQuestionHandler
from app.ports import RetrievedChunk
from app.testing.fakes import FakeEmbedder, FakeLLM, FakeRetriever


def test_low_relevance_chunks_are_excluded() -> None:
    retriever = FakeRetriever(results=[
        RetrievedChunk(text="on-topic passage", score=0.88),
        RetrievedChunk(text="unrelated passage", score=0.22),
    ])
    handler = AnswerQuestionHandler(
        llm=FakeLLM(response="grounded answer"),
        embedder=FakeEmbedder(),
        retriever=retriever,
    )

    result = handler.handle(AnswerQuestionQuery(question="what does the policy say?", min_relevance=0.5))

    assert "unrelated passage" not in result.chunks_used
    assert "on-topic passage" in result.chunks_used


def test_nothing_relevant_means_no_llm_call() -> None:
    llm = FakeLLM()
    handler = AnswerQuestionHandler(
        llm=llm, embedder=FakeEmbedder(), retriever=FakeRetriever([RetrievedChunk("weak", 0.2)])
    )
    result = handler.handle(AnswerQuestionQuery(question="anything", min_relevance=0.5))
    assert result.answer == NO_GROUNDED_ANSWER
    assert llm.prompts == []
