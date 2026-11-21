# tests/test_answer_graph.py — 5.3, the graph drives the core through ports
from app.adapters.orchestration.answer_graph import build_answer_graph
from app.core.query_handler import NO_GROUNDED_ANSWER, AnswerQuestionHandler
from app.ports import RetrievedChunk
from app.testing.fakes import FakeEmbedder, FakeLLM, FakeRetriever


def make_handler(results: list[RetrievedChunk], llm: FakeLLM | None = None) -> AnswerQuestionHandler:
    return AnswerQuestionHandler(
        llm=llm or FakeLLM("grounded"), embedder=FakeEmbedder(), retriever=FakeRetriever(results)
    )


def test_sufficient_context_answers_in_one_pass() -> None:
    graph = build_answer_graph(make_handler([RetrievedChunk("policy text", 0.9)]))
    state = graph.invoke({"question": "what does the policy say?"})
    assert state["verdict"] == "sufficient"
    assert state["answer"] == "grounded"
    assert state["attempts"] == 1


def test_insufficient_context_retries_then_stops() -> None:
    retriever = FakeRetriever([RetrievedChunk("weak", 0.1)])
    handler = AnswerQuestionHandler(llm=FakeLLM("x"), embedder=FakeEmbedder(), retriever=retriever)
    graph = build_answer_graph(handler, max_attempts=3)

    state = graph.invoke({"question": "unknowable"})

    assert state["attempts"] == 3          # the loop has a stopping rule
    assert retriever.calls == 3
    assert state["answer"] == NO_GROUNDED_ANSWER


def test_with_an_llm_port_the_graph_classifies_and_reformulates() -> None:
    graph_llm = FakeLLM("yes — rewritten question")
    graph = build_answer_graph(make_handler([RetrievedChunk("weak", 0.1)]), llm=graph_llm, max_attempts=2)

    state = graph.invoke({"question": "compare 2022 and 2023"})

    assert state["is_comparative"] is True
    assert state["question"] == "yes — rewritten question"  # reformulated before the retry
    assert any("Rewrite this question" in p for p in graph_llm.prompts)
