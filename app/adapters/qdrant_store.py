# app/adapters/qdrant_store.py — VectorStorePort (3.4, 3.5) and RetrievalPort (4.3) implementations
#
# Qdrant ids must be integers or UUIDs, so the domain key ("doc-42-3") is
# mapped to a stable UUID and kept in the payload, together with its
# document prefix ("doc-42") so delete_prefix can remove a whole document.
# Pass url=":memory:" to run Qdrant in-process (tests, demos).
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    FilterSelector,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.ports import RetrievalPort, RetrievedChunk, VectorStorePort


def point_id(key: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, key))


def document_prefix(key: str) -> str:
    return key.rsplit("-", 1)[0]


class QdrantVectorStore(VectorStorePort):
    """Command side: strict, immediately consistent writes."""

    def __init__(self, url: str, collection: str, client: QdrantClient | None = None) -> None:
        self._client = client or QdrantClient(location=url)
        self._collection = collection

    def _ensure_collection(self, size: int) -> None:
        if not self._client.collection_exists(self._collection):
            self._client.create_collection(
                self._collection, vectors_config=VectorParams(size=size, distance=Distance.COSINE)
            )

    def upsert(self, key: str, embedding: list[float], metadata: dict) -> None:
        self._ensure_collection(len(embedding))
        payload = {**metadata, "key": key, "prefix": document_prefix(key)}
        self._client.upsert(
            self._collection, points=[PointStruct(id=point_id(key), vector=embedding, payload=payload)]
        )

    def delete_prefix(self, prefix: str) -> None:
        if not self._client.collection_exists(self._collection):
            return
        selector = FilterSelector(
            filter=Filter(must=[FieldCondition(key="prefix", match=MatchValue(value=prefix))])
        )
        self._client.delete(self._collection, points_selector=selector)


class QdrantRetriever(RetrievalPort):
    """Query side. Can point at the same Qdrant as the writer, or at a read replica."""

    def __init__(self, url: str, collection: str, client: QdrantClient | None = None) -> None:
        self._client = client or QdrantClient(location=url)
        self._collection = collection

    def search(self, embedding: list[float], top_k: int) -> list[RetrievedChunk]:
        if not self._client.collection_exists(self._collection):
            return []
        response = self._client.query_points(
            self._collection, query=embedding, limit=top_k, with_payload=True
        )
        return [
            RetrievedChunk(text=str((p.payload or {}).get("text", "")), score=p.score)
            for p in response.points
        ]
