# tests/test_review_flow.py — 5.4, a pause that survives between requests
from fastapi.testclient import TestClient
from langgraph.checkpoint.memory import InMemorySaver

from app.adapters.api.http_handler import create_api
from app.composition import wire
from app.config import Settings
from app.testing.fakes import FakeEmbedder, FakeLLM, FakeRetriever, FakeStructuredQueryPort, FakeVectorStore


def make_client() -> tuple[TestClient, FakeVectorStore]:
    store = FakeVectorStore()
    application = wire(
        Settings(), FakeLLM(), FakeEmbedder(), store, FakeRetriever(), FakeStructuredQueryPort(), InMemorySaver()
    )
    return TestClient(create_api(application)), store


def test_nothing_is_ingested_until_a_person_approves() -> None:
    client, store = make_client()

    submitted = client.post("/ingest/doc-1/submit", json={"text": "contract text " * 50})
    assert submitted.json() == {"doc_id": "doc-1", "status": "pending_review"}
    assert store.rows == {}  # paused before "ingest" — nothing written

    approved = client.post("/ingest/doc-1/approve")
    assert approved.json()["status"] == "ingested"
    assert any(key.startswith("doc-1-") for key in store.rows)


def test_a_rejected_document_is_never_ingested() -> None:
    client, store = make_client()
    client.post("/ingest/doc-2/submit", json={"text": "draft"})

    assert client.post("/ingest/doc-2/reject").json()["status"] == "rejected"
    assert store.rows == {}


def test_reviews_are_independent_threads() -> None:
    client, store = make_client()
    client.post("/ingest/a/submit", json={"text": "first"})
    client.post("/ingest/b/submit", json={"text": "second"})

    client.post("/ingest/b/approve")

    assert set(store.rows) == {"b-0"}
