# tests/test_end_to_end.py — 7.1, one request through the complete system
#
# The real composition root, the real adapters (offline set), the real
# graphs and wrappers — driven over HTTP exactly like production.
import pathlib
import sqlite3

import pytest
from fastapi.testclient import TestClient

from app.adapters.api.http_handler import create_api
from app.composition import build_application
from app.config import Settings

SAMPLES = pathlib.Path(__file__).resolve().parents[1] / "data" / "sample"


@pytest.fixture()
def client(tmp_path: pathlib.Path) -> TestClient:
    db = tmp_path / "catalog.sqlite3"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE documents (doc_id TEXT, year INTEGER)")
        conn.executemany("INSERT INTO documents VALUES (?, ?)", [("a", 2022), ("b", 2023)])
    settings = Settings(
        deployment_mode="offline",
        min_relevance_threshold=0.2,
        structured_database_url=f"sqlite:///{db}",
        nlq_schema="documents(doc_id TEXT, year INTEGER)",
        judge_sample_rate=0.0,
    )
    client = TestClient(create_api(build_application(settings)))
    for path in sorted(SAMPLES.glob("*.md")):
        assert client.post("/ingest", json={"doc_id": path.stem, "text": path.read_text()}).json()["succeeded"]
    return client


def test_query_answers_from_the_right_document(client: TestClient) -> None:
    response = client.post("/query", json={"text": "How much is the hotel reimbursed per night in 2023?"})
    body = response.json()
    assert body["answer"] == "Hotel stays are reimbursed up to 180 dollars per night."
    assert body["checks"] == []  # 6.1: grounded, cited, not empty
    assert body["trace_id"]       # 6.2: every answer is traceable


def test_unanswerable_question_is_refused_not_hallucinated(client: TestClient) -> None:
    body = client.post("/query", json={"text": "zebra quantum saxophone"}).json()
    assert body["chunks_used"] == []
    assert body["checks"] == ["answer_without_citations"]


def test_router_sends_counting_questions_to_the_database(client: TestClient) -> None:
    body = client.post("/route", json={"text": "How many documents are there?"}).json()
    assert body["route"] == "structured"
    assert "2" in body["answer"]


def test_review_then_ingest(client: TestClient) -> None:
    assert client.post("/ingest/new-doc/submit", json={"text": "Bonus policy."}).json()["status"] == "pending_review"
    assert client.post("/ingest/new-doc/approve").json()["status"] == "ingested"


def test_pii_is_redacted_before_the_model(client: TestClient) -> None:
    answer = client.post("/query", json={"text": "Who do I contact at people@example.com?"}).json()["answer"]
    assert "people@example.com" not in answer
