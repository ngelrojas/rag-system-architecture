# tests/test_outbox.py — 3.8, with a fake connection that records transactions
from collections.abc import Iterator
from contextlib import contextmanager
from types import SimpleNamespace
from typing import Any

from app.adapters.postgres_outbox_store import PostgresVectorStoreWithOutbox
from relay import relay_once


class RecordingConnection:
    def __init__(self, rows: list[Any] | None = None) -> None:
        self.transactions: list[list[str]] = []
        self.statements: list[str] = []
        self._current: list[str] | None = None
        self._rows = rows or []

    @contextmanager
    def transaction(self) -> Iterator[None]:
        self._current = []
        yield
        self.transactions.append(self._current)
        self._current = None

    def execute(self, sql: str, params: tuple = ()) -> SimpleNamespace:
        (self._current if self._current is not None else self.statements).append(sql)
        return SimpleNamespace(fetchall=lambda: self._rows)


def test_chunk_and_event_are_written_in_one_transaction() -> None:
    db = RecordingConnection()
    PostgresVectorStoreWithOutbox(db).upsert("doc-1-0", [0.1, 0.2], {"text": "hello"})

    assert len(db.transactions) == 1
    chunk_insert, outbox_insert = db.transactions[0]
    assert chunk_insert.startswith("INSERT INTO chunks")
    assert outbox_insert.startswith("INSERT INTO outbox")


def test_delete_prefix_also_emits_its_event_atomically() -> None:
    db = RecordingConnection()
    PostgresVectorStoreWithOutbox(db).delete_prefix("doc-1")
    assert [s.split()[0] for s in db.transactions[0]] == ["DELETE", "INSERT"]


def test_relay_publishes_then_marks_published() -> None:
    rows = [SimpleNamespace(id="e1", event_type="chunk_ingested", payload='{"key": "doc-1-0"}')]
    db = RecordingConnection(rows=rows)
    published: list[tuple[str, str]] = []
    queue = SimpleNamespace(publish=lambda topic, payload: published.append((topic, payload)))

    assert relay_once(db, queue) == 1
    assert published == [("chunk_ingested", '{"key": "doc-1-0"}')]
    assert db.statements[-1].startswith("UPDATE outbox SET published = true")
