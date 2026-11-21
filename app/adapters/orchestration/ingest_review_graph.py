# app/adapters/orchestration/ingest_review_graph.py — 5.4
#
# Same rules as answer_graph.py from 5.3: driving adapter, no direct
# adapter imports, GraphState holds only what must cross the pause.
#
# The pause is the checkpointer's job, not the node's: the graph is
# compiled with interrupt_before=["ingest"], so after "review" runs,
# LangGraph persists the state and returns control to the caller.
# A later call — another request, another process, days later —
# records the decision with update_state and resumes with invoke(None).
from typing import Any, Literal, TypedDict

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, StateGraph

from app.core.commands import IngestDocumentCommand
from app.core.ingest_handler import IngestDocumentHandler

ReviewStatus = Literal["pending", "approved", "rejected", "ingested", "failed"]


class ReviewGraphState(TypedDict):
    doc_id: str
    text: str
    review_status: ReviewStatus


def build_ingest_review_graph(handler: IngestDocumentHandler, checkpointer: BaseCheckpointSaver) -> Any:
    def request_review_node(state: ReviewGraphState) -> dict:
        # This node does NOT block. It marks state and returns —
        # the graph's own machinery persists everything via the checkpointer.
        return {"review_status": "pending"}

    def ingest_node(state: ReviewGraphState) -> dict:
        # Only runs after a person has decided. Calls the CORE,
        # exactly as answer_graph.py did in 5.3.
        if state["review_status"] != "approved":
            return {"review_status": "rejected"}
        result = handler.handle(IngestDocumentCommand(doc_id=state["doc_id"], text=state["text"]))
        return {"review_status": "ingested" if result.succeeded else "failed"}

    graph = StateGraph(ReviewGraphState)
    graph.add_node("review", request_review_node)
    graph.add_node("ingest", ingest_node)
    graph.set_entry_point("review")
    graph.add_edge("review", "ingest")
    graph.add_edge("ingest", END)

    # interrupt_before tells LangGraph to persist state and return control
    # to the caller BEFORE running "ingest", instead of blocking on it.
    return graph.compile(checkpointer=checkpointer, interrupt_before=["ingest"])
