# app/compliance/sql_guardrail.py — 6.3
#
# Wraps a database port, exactly the same composition pattern as
# TracedLLMPort from 6.2 — but this wrapper can refuse to proceed.
import re

from app.ports import StructuredQueryPort

FORBIDDEN_PATTERNS = re.compile(
    r"\b(DROP|DELETE|UPDATE|INSERT|ALTER|TRUNCATE|GRANT|REVOKE|CREATE|REPLACE|MERGE|ATTACH|PRAGMA)\b",
    re.IGNORECASE,
)


class ComplianceError(Exception):
    pass


class ReadOnlySqlGuardrail(StructuredQueryPort):
    """Wraps any StructuredQueryPort implementation. Blocks any query
    containing a mutating SQL keyword before it ever reaches the database."""

    def __init__(self, inner: StructuredQueryPort):
        self._inner = inner

    def execute(self, sql: str) -> list[dict]:
        if FORBIDDEN_PATTERNS.search(sql) or ";" in sql.strip().rstrip(";"):
            raise ComplianceError(f"Blocked mutating SQL from NLQ path: {sql[:80]}...")
        return self._inner.execute(sql)
