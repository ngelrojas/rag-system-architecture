# app/adapters/orchestration/answer_graph.py — 5.3
#
# This file is a driving adapter, exactly like an HTTP handler.
# It is allowed to import LangGraph. It is NOT allowed to import
# app/adapters/openai_llm.py or app/adapters/qdrant_store.py directly —
# the import-linter contracts apply to this file too.
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from app.core.queries import AnswerQuestionQuery
from app.core.query_handler import AnswerQuestionHandler
from app.ports import LLMPort


class GraphState(TypedDict, total=False):
    question: str         # the question as currently phrased
    attempts: int         # how many answer passes have run
    is_comparative: bool  # set by the optional classify node
    verdict: str          # only what must cross node boundaries
    answer: str           # nothing else — no raw candidates, no client objects


def build_answer_graph(
    handler: AnswerQuestionHandler,   # high-level: full retrieve + generate
    llm: LLMPort | None = None,       # low-level: classify and reformulate (optional)
    min_relevance: float = 0.5,
    max_attempts: int = 2,
) -> Any:
    """
    Takes an already-constructed AnswerQuestionHandler — built by the
    composition root, exactly as in 3.4 — and wraps it in a graph.
    The graph never constructs a handler itself.
    """

    def classify_node(state: GraphState) -> dict:
        # Legitimate: llm is a PORT, injected, not a concrete client.
        # This node needs the LLM alone, without a full handler pass.
        assert llm is not None
        verdict = llm.complete(f"Is this question comparative? Answer yes or no. '{state['question']}'")
        return {"is_comparative": "yes" in verdict.lower()}

    def answer_node(state: GraphState) -> dict:
        # Calls the CORE, not an adapter. The handler internally uses
        # RetrievalPort and LLMPort — this node never sees either one.
        result = handler.handle(AnswerQuestionQuery(question=state["question"], min_relevance=min_relevance))
        verdict = "sufficient" if result.chunks_used else "insufficient"
        return {"verdict": verdict, "answer": result.answer, "attempts": state.get("attempts", 0) + 1}

    def reformulate_node(state: GraphState) -> dict:
        # The corrective step: rephrase the question for retrieval and try again.
        assert llm is not None
        rewritten = llm.complete(
            "Rewrite this question so a document search is more likely to find the answer. "
            f"Return only the rewritten question.\n\n{state['question']}"
        )
        return {"question": rewritten.strip() or state["question"]}

    def route(state: GraphState) -> str:
        if state["verdict"] == "sufficient" or state.get("attempts", 0) >= max_attempts:
            return "end"  # a corrective loop needs a stopping rule, or it never ends
        return "retry"

    graph = StateGraph(GraphState)
    graph.add_node("answer", answer_node)
    retry_target = "answer"
    if llm is not None:
        graph.add_node("classify", classify_node)
        graph.add_node("reformulate", reformulate_node)
        graph.add_edge("reformulate", "answer")
        graph.set_entry_point("classify")
        graph.add_edge("classify", "answer")
        retry_target = "reformulate"
    else:
        graph.set_entry_point("answer")
    graph.add_conditional_edges("answer", route, {"end": END, "retry": retry_target})
    return graph.compile()
