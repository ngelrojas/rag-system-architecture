# adapters/qdrant_store.py — 2.4
#
# Qdrant's ids must be integers or UUIDs, so the domain's chunk id
# ("doc-42-3") is mapped to a stable UUID and kept in the payload.
# Pass url=":memory:" to run Qdrant in-process (tests, demos).
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from domain.ports import Match


def point_id(key: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, key))


class QdrantVectorStore:
    def __init__(self, url: str, collection: str) -> None:
        self._client = QdrantClient(location=url)
        self._collection = collection

    def _ensure_collection(self, size: int) -> None:
        if not self._client.collection_exists(self._collection):
            self._client.create_collection(
                self._collection, vectors_config=VectorParams(size=size, distance=Distance.COSINE)
            )

    def upsert(self, id: str, vector: list[float], metadata: dict) -> None:
        self._ensure_collection(len(vector))
        self._client.upsert(
            self._collection,
            points=[PointStruct(id=point_id(id), vector=vector, payload={**metadata, "key": id})],
        )

    def query(self, vector: list[float], top_k: int) -> list[Match]:
        if not self._client.collection_exists(self._collection):
            return []
        response = self._client.query_points(self._collection, query=vector, limit=top_k, with_payload=True)
        hits = response.points
        return [
            Match(id=str((h.payload or {}).get("key", h.id)), score=h.score, metadata=dict(h.payload or {}))
            for h in hits
        ]
