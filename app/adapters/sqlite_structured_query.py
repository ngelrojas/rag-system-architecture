# app/adapters/sqlite_structured_query.py — StructuredQueryPort on SQLite (5.5)
#
# Standard library only: handy for tests and the offline demo. Production
# uses PostgresStructuredQuery; the handler cannot tell the difference.
import sqlite3

from app.ports import StructuredQueryPort


class SqliteStructuredQuery(StructuredQueryPort):
    def __init__(self, path: str = ":memory:", connection: sqlite3.Connection | None = None) -> None:
        self._conn = connection or sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row

    def execute(self, sql: str) -> list[dict]:
        return [dict(row) for row in self._conn.execute(sql).fetchall()]
