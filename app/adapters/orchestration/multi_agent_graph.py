# app/adapters/orchestration/multi_agent_graph.py — 5.5
#
# Same rules as every other file in Part V: driving adapter, lives outside
# app/core, calls only existing handler interfaces and ports.
from typing import Any, Literal, TypedDict

from langgraph.graph import END, StateGraph

from app.core.queries import AnswerQuestionQuery
from app.core.query_handler import AnswerQuestionHandler
from app.core.structured_queries import StructuredQuery
from app.core.structured_query_handler import StructuredQueryHandler
from app.ports import LLMPort


class RoutingState(TypedDict, total=False):
    question: str
    route: Literal["semantic", "structured", "both"]
    semantic_answer: str | None
    structured_answer: str | None
    final_answer: str


def build_multi_agent_graph(
    answer_handler: AnswerQuestionHandler,
    structured_handler: StructuredQueryHandler,
    llm: LLMPort,
    min_relevance: float = 0.5,
) -> Any:
    def classify_node(state: RoutingState) -> dict:
        # A routing decision, not a domain decision. It calls the LLM to
        # classify — the same LLMPort every other node in Part V has used —
        # and produces nothing the domain core would ever need to know about.
        verdict = llm.complete(
            f"Does this question need document search, a database count, or both? '{state['question']}'"
        ).lower()
        route = "both" if "both" in verdict else ("structured" if "count" in verdict else "semantic")
        return {"route": route}

    def semantic_node(state: RoutingState) -> dict:
        # Calls the CORE. Same handler, same interface, since Part IV.
        result = answer_handler.handle(AnswerQuestionQuery(question=state["question"], min_relevance=min_relevance))
        return {"semantic_answer": result.answer}

    def structured_node(state: RoutingState) -> dict:
        result = structured_handler.handle(StructuredQuery(question=state["question"]))
        return {"structured_answer": result.answer}

    def synthesize_node(state: RoutingState) -> dict:
        semantic, structured = state.get("semantic_answer"), state.get("structured_answer")
        if structured is None:
            return {"final_answer": semantic or ""}
        if semantic is None:
            return {"final_answer": structured}
        # Only reached when BOTH paths ran — this is the only place
        # combining two results is actually needed.
        combined = llm.complete(f"Combine these into one answer: {semantic} / {structured}")
        return {"final_answer": combined}

    def route_after_classify(state: RoutingState) -> list[str]:
        if state["route"] == "semantic":
            return ["semantic"]
        if state["route"] == "structured":
            return ["structured"]
        return ["semantic", "structured"]  # both paths run in parallel

    graph = StateGraph(RoutingState)
    graph.add_node("classify", classify_node)
    graph.add_node("semantic", semantic_node)
    graph.add_node("structured", structured_node)
    graph.add_node("synthesize", synthesize_node)
    graph.set_entry_point("classify")
    graph.add_conditional_edges("classify", route_after_classify, ["semantic", "structured"])
    graph.add_edge("semantic", "synthesize")
    graph.add_edge("structured", "synthesize")
    graph.add_edge("synthesize", END)
    return graph.compile()
