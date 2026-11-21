# tests/test_compliance.py — 6.3
import pytest

from app.compliance.pii_guardrail import PiiGuardrailLLM
from app.compliance.sql_guardrail import ComplianceError, ReadOnlySqlGuardrail
from app.testing.fakes import FakeLLM, FakeStructuredQueryPort


@pytest.mark.parametrize(
    "sql",
    ["DROP TABLE documents", "delete from documents", "UPDATE t SET x = 1", "SELECT 1; DROP TABLE t"],
)
def test_mutating_sql_never_reaches_the_database(sql: str) -> None:
    db = FakeStructuredQueryPort()
    with pytest.raises(ComplianceError):
        ReadOnlySqlGuardrail(db).execute(sql)
    assert db.executed == []


def test_reads_pass_through() -> None:
    db = FakeStructuredQueryPort(rows=[{"n": 3}])
    assert ReadOnlySqlGuardrail(db).execute("SELECT COUNT(*) AS n FROM documents") == [{"n": 3}]


def test_the_model_never_sees_raw_pii() -> None:
    model = FakeLLM("ok")
    PiiGuardrailLLM(model).complete("Contact ana@example.com, SSN 123-45-6789, CPF 123.456.789-09.")
    sent = model.prompts[0]
    assert "ana@example.com" not in sent and "123-45-6789" not in sent and "123.456.789-09" not in sent
    assert "[REDACTED-EMAIL]" in sent and "[REDACTED-SSN]" in sent and "[REDACTED-CPF]" in sent
