# tests/test_qdrant_store.py — the real adapter, against in-process Qdrant
from adapters.qdrant_store import QdrantVectorStore
from domain.ports import VectorStorePort


def test_upsert_then_query_round_trip() -> None:
    store: VectorStorePort = QdrantVectorStore(url=":memory:", collection="chunks")
    store.upsert("doc-0", [1.0, 0.0], {"text": "about cats"})
    store.upsert("doc-1", [0.0, 1.0], {"text": "about dogs"})

    matches = store.query([0.9, 0.1], top_k=1)

    assert matches[0].id == "doc-0"
    assert matches[0].metadata["text"] == "about cats"


def test_upsert_replaces_the_same_id() -> None:
    store = QdrantVectorStore(url=":memory:", collection="chunks")
    store.upsert("doc-0", [1.0, 0.0], {"text": "old"})
    store.upsert("doc-0", [1.0, 0.0], {"text": "new"})
    assert [m.metadata["text"] for m in store.query([1.0, 0.0], top_k=5)] == ["new"]
