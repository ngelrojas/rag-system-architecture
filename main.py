# main.py — application entry point (3.4)
#
#   uv run uvicorn main:api --reload
#
# The book's sketch awaits the handlers; the handlers in this repository
# are synchronous, so FastAPI runs the endpoints in its thread pool.
from fastapi import FastAPI
from pydantic import BaseModel

from app.composition import build_application
from app.config import Settings

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
    result = app_deps.query_handler.handle(request.text)
    return {"answer": result.answer, "chunks_used": result.chunks_used}


@api.post("/ingest")
def ingest_endpoint(request: IngestRequest) -> dict:
    result = app_deps.ingest_handler.handle(doc_id=request.doc_id, text=request.text)
    return {"doc_id": result.doc_id, "chunks_ingested": result.chunks_ingested, "succeeded": result.succeeded}
