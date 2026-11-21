# main.py — application entry point (3.4; commands and queries since 4.4)
#
#   uv run uvicorn main:api --reload
from fastapi import FastAPI
from pydantic import BaseModel

from app.composition import build_application
from app.config import Settings
from app.core.commands import IngestDocumentCommand
from app.core.queries import AnswerQuestionQuery

settings = Settings()  # reads env vars, .env, etc.
app_deps = build_application(settings)

api = FastAPI(title="Document intelligence service")


class QueryRequest(BaseModel):
    text: str


class IngestRequest(BaseModel):
    doc_id: str
    text: str


@api.post("/query")
def query_endpoint(request: QueryRequest) -> dict:
    query = AnswerQuestionQuery(question=request.text, min_relevance=settings.min_relevance_threshold)
    result = app_deps.query_handler.handle(query)
    return {"answer": result.answer, "chunks_used": result.chunks_used}


@api.post("/ingest")
def ingest_endpoint(request: IngestRequest) -> dict:
    result = app_deps.ingest_handler.handle(IngestDocumentCommand(doc_id=request.doc_id, text=request.text))
    return {"doc_id": result.doc_id, "chunks_ingested": result.chunks_ingested, "succeeded": result.succeeded}
