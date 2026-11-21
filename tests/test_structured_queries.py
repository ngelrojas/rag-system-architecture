# tests/test_structured_queries.py — 5.5, NLQ behind two ports
import sqlite3

from app.adapters.sqlite_structured_query import SqliteStructuredQuery
from app.core.structured_queries import StructuredQuery
from app.core.structured_query_handler import StructuredQueryHandler, extract_sql
from app.testing.fakes import ScriptedLLM


def test_handler_writes_sql_runs_it_and_phrases_the_answer() -> None:
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE documents (doc_id TEXT, year INTEGER)")
    conn.executemany("INSERT INTO documents VALUES (?, ?)", [("a", 2022), ("b", 2023), ("c", 2023)])
    llm = ScriptedLLM(["```sql\nSELECT COUNT(*) AS n FROM documents WHERE year = 2023;\n```", "There are 2."])
    db = SqliteStructuredQuery(connection=conn)
    handler = StructuredQueryHandler(llm=llm, db=db, schema="documents(doc_id, year)")

    result = handler.handle(StructuredQuery(question="How many documents are from 2023?"))

    assert result.sql == "SELECT COUNT(*) AS n FROM documents WHERE year = 2023"
    assert result.rows == [{"n": 2}]
    assert result.answer == "There are 2."
    assert "documents(doc_id, year)" in llm.prompts[0]


def test_extract_sql_strips_fences_and_semicolons() -> None:
    assert extract_sql("```SQL\nSELECT 1;\n```") == "SELECT 1"
    assert extract_sql("SELECT 2") == "SELECT 2"
