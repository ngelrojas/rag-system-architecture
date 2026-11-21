# app/adapters/api/http_handler.py — the HTTP driving adapter (3.4, moved here in 5.4)
#
# Receives an already-wired Application from the composition root and
# exposes it over HTTP. Like every driving adapter, it calls the core's
# handlers and graphs, never a concrete driven adapter.
from fastapi import FastAPI
from pydantic import BaseModel

from app.adapters.api.review_endpoints import build_review_router
from app.application import Application
from app.core.commands import IngestDocumentCommand
from app.core.queries import AnswerQuestionQuery


class QueryRequest(BaseModel):
    text: str


class IngestRequest(BaseModel):
    doc_id: str
    text: str


def create_api(application: Application) -> FastAPI:
    api = FastAPI(title="Document intelligence service")

    @api.post("/query")
    def query_endpoint(request: QueryRequest) -> dict:
        query = AnswerQuestionQuery(question=request.text, min_relevance=application.min_relevance)
        result = application.query_handler.handle(query)
        return {"answer": result.answer, "chunks_used": result.chunks_used}

    @api.post("/ask")
    def ask_endpoint(request: QueryRequest) -> dict:
        # The same question, through the corrective answer graph (5.3).
        state = application.answer_graph.invoke({"question": request.text})
        return {"answer": state["answer"], "attempts": state["attempts"]}

    @api.post("/route")
    def route_endpoint(request: QueryRequest) -> dict:
        # Documents, database, or both — decided by the multi-agent graph (5.5).
        state = application.multi_agent_graph.invoke({"question": request.text})
        return {"answer": state["final_answer"], "route": state["route"]}

    @api.post("/ingest")
    def ingest_endpoint(request: IngestRequest) -> dict:
        result = application.ingest_handler.handle(IngestDocumentCommand(doc_id=request.doc_id, text=request.text))
        return {"doc_id": result.doc_id, "chunks_ingested": result.chunks_ingested, "succeeded": result.succeeded}

    api.include_router(build_review_router(application.review_graph))
    return api
