# app/adapters/postgres_structured_query.py — StructuredQueryPort on Postgres (5.5)
import psycopg
from psycopg.rows import dict_row

from app.ports import StructuredQueryPort


class PostgresStructuredQuery(StructuredQueryPort):
    def __init__(self, connection_string: str) -> None:
        self._connection_string = connection_string

    def execute(self, sql: str) -> list[dict]:
        with psycopg.connect(self._connection_string, row_factory=dict_row) as conn:
            return list(conn.execute(sql).fetchall())
