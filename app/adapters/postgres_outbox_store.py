# app/adapters/postgres_outbox_store.py — 3.8
#
# Writes the chunk AND an outbox event in one local transaction: an event
# is never written without its data, because they are the same commit.
#
# db_connection is a psycopg 3 connection (anything with .transaction()
# and .execute() works, which is how the tests use a fake).
import json
import uuid
from typing import Any

from app.ports import RetrievedChunk, VectorStorePort


class PostgresVectorStoreWithOutbox(VectorStorePort):
    """Writes the document AND an outbox event in one local transaction."""

    def __init__(self, db_connection: Any):
        self._db = db_connection

    def upsert(self, key: str, embedding: list[float], metadata: dict) -> None:
        with self._db.transaction():
            self._db.execute(
                "INSERT INTO chunks (key, embedding, metadata) VALUES (%s, %s, %s) "
                "ON CONFLICT (key) DO UPDATE SET embedding = EXCLUDED.embedding, metadata = EXCLUDED.metadata",
                (key, embedding, json.dumps(metadata)),
            )
            # Same transaction — either both rows land, or neither does.
            self._db.execute(
                "INSERT INTO outbox (id, event_type, payload, published) VALUES (%s, %s, %s, false)",
                (str(uuid.uuid4()), "chunk_ingested", json.dumps({"key": key})),
            )

    def delete_prefix(self, prefix: str) -> None:
        with self._db.transaction():
            self._db.execute("DELETE FROM chunks WHERE key LIKE %s", (f"{prefix}%",))
            self._db.execute(
                "INSERT INTO outbox (id, event_type, payload, published) VALUES (%s, %s, %s, false)",
                (str(uuid.uuid4()), "chunks_deleted", json.dumps({"prefix": prefix})),
            )

    def search(self, embedding: list[float], top_k: int) -> list[RetrievedChunk]:
        # This adapter is the write side of ingestion. Searching stays with
        # the vector store; Part IV (4.3) makes that split explicit by giving
        # the read side its own port.
        raise NotImplementedError("PostgresVectorStoreWithOutbox is write-only; search with QdrantVectorStore")
