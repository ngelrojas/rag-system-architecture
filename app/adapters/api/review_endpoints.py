# app/adapters/api/review_endpoints.py — where the two halves connect (5.4)
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel


class SubmitRequest(BaseModel):
    text: str


def build_review_router(graph: Any) -> APIRouter:
    router = APIRouter(prefix="/ingest", tags=["review"])

    def config(doc_id: str) -> Any:
        return {"configurable": {"thread_id": doc_id}}

    @router.post("/{doc_id}/submit")
    def submit_for_review(doc_id: str, request: SubmitRequest) -> dict:
        graph.invoke({"doc_id": doc_id, "text": request.text, "review_status": "pending"}, config=config(doc_id))
        # Execution stops at the interrupt_before boundary. Nothing is blocked —
        # this endpoint returns immediately with a pending status.
        return {"doc_id": doc_id, "status": "pending_review"}

    @router.post("/{doc_id}/approve")
    def approve_review(doc_id: str) -> dict:
        # Loads the checkpoint written by the FIRST call, potentially in a
        # completely different process, potentially days later.
        graph.update_state(config(doc_id), {"review_status": "approved"})
        result = graph.invoke(None, config=config(doc_id))
        return {"doc_id": doc_id, "status": result["review_status"]}

    @router.post("/{doc_id}/reject")
    def reject_review(doc_id: str) -> dict:
        graph.update_state(config(doc_id), {"review_status": "rejected"})
        result = graph.invoke(None, config=config(doc_id))
        return {"doc_id": doc_id, "status": result["review_status"]}

    return router
