# scripts/demo.py — the complete reference system, end to end, offline (7.1)
#
#   make demo          (or: uv run python -m scripts.demo)
#
# Builds the real application through the real composition root, in
# DEPLOYMENT_MODE=offline — in-process Qdrant, hashing embeddings and an
# extractive model — then exercises every driving path over HTTP.
import logging
import pathlib
import sqlite3
import tempfile

import structlog
from fastapi.testclient import TestClient

from app.adapters.api.http_handler import create_api
from app.composition import build_application
from app.config import Settings

SAMPLES = pathlib.Path(__file__).resolve().parents[1] / "data" / "sample"


def spans(enabled: bool) -> None:
    level = logging.INFO if enabled else logging.WARNING
    structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(level))


def main() -> None:
    spans(enabled=False)  # quiet by default; the observability section turns spans on
    db_path = pathlib.Path(tempfile.mkdtemp()) / "catalog.sqlite3"
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE documents (doc_id TEXT, title TEXT, year INTEGER)")
        conn.executemany(
            "INSERT INTO documents VALUES (?, ?, ?)",
            [("travel-policy-2022", "Travel Policy", 2022), ("travel-policy-2023", "Travel Policy", 2023),
             ("remote-work-policy", "Remote Work Policy", 2023)],
        )

    settings = Settings(
        deployment_mode="offline",
        min_relevance_threshold=0.2,
        chunk_size=400,
        structured_database_url=f"sqlite:///{db_path}",
        nlq_schema="documents(doc_id TEXT, title TEXT, year INTEGER)",
        judge_sample_rate=0.0,
    )
    client = TestClient(create_api(build_application(settings)))

    print("== Ingest (command side, 4.4)")
    for path in sorted(SAMPLES.glob("*.md")):
        print(" ", client.post("/ingest", json={"doc_id": path.stem, "text": path.read_text()}).json())

    print("\n== Query (query side, with 6.1 checks and a 6.2 trace_id)")
    for question in ["How much is the hotel reimbursed per night in 2023?", "What are the core hours for remote work?"]:
        r = client.post("/query", json={"text": question}).json()
        print(f"  Q: {question}\n  A: {r['answer']}\n     checks={r['checks']} trace_id={r['trace_id']}")

    print("\n== Ask (corrective answer graph, 5.3)")
    print(" ", client.post("/ask", json={"text": "Which class can I book for flights of six hours or more?"}).json())

    print("\n== Observability (6.2): one request, reconstructed from its spans")
    spans(enabled=True)
    client.post("/query", json={"text": "How much are meals reimbursed per day?"}, headers={"X-Trace-Id": "demo-trace"})
    spans(enabled=False)

    print("\n== Route (multi-agent graph: documents or database, 5.5)")
    print(" ", client.post("/route", json={"text": "How many documents are in the catalog?"}).json())

    print("\n== Human-in-the-loop review (5.4)")
    print(" ", client.post("/ingest/expense-policy/submit", json={"text": "Draft expense policy."}).json())
    print(" ", client.post("/ingest/expense-policy/approve").json())

    print("\n== Compliance (6.3): PII never reaches the model")
    print(" ", client.post("/query", json={"text": "Who do I contact at people@example.com?"}).json()["answer"])


if __name__ == "__main__":
    main()
