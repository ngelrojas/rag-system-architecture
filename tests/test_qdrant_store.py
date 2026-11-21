# tests/test_qdrant_store.py — the real adapters, against in-process Qdrant
from qdrant_client import QdrantClient

from app.adapters.cached_retriever import CachedRetriever
from app.adapters.qdrant_store import QdrantRetriever, QdrantVectorStore
from app.ports import RetrievalPort, VectorStorePort


def make_pair() -> tuple[VectorStorePort, RetrievalPort]:
    client = QdrantClient(location=":memory:")  # one in-process Qdrant shared by both sides
    return (
        QdrantVectorStore(url=":memory:", collection="chunks", client=client),
        QdrantRetriever(url=":memory:", collection="chunks", client=client),
    )


def test_write_side_then_read_side() -> None:
    store, retriever = make_pair()
    store.upsert("doc-0", [1.0, 0.0], {"text": "about cats"})
    store.upsert("doc-1", [0.0, 1.0], {"text": "about dogs"})

    results = retriever.search([0.9, 0.1], top_k=1)

    assert results[0].text == "about cats"
    assert results[0].score > 0.9


def test_delete_prefix_removes_a_whole_document() -> None:
    store, retriever = make_pair()
    for i in range(3):
        store.upsert(f"policy-{i}", [1.0, float(i)], {"text": f"policy part {i}"})
    store.upsert("other-0", [1.0, 0.0], {"text": "unrelated"})

    store.delete_prefix("policy")

    assert [r.text for r in retriever.search([1.0, 0.0], top_k=10)] == ["unrelated"]


def test_cached_retriever_serves_repeats_from_cache() -> None:
    store, retriever = make_pair()
    store.upsert("doc-0", [1.0, 0.0], {"text": "cached"})
    cached = CachedRetriever(inner=retriever, ttl_s=60)

    first = cached.search([1.0, 0.0], top_k=1)
    store.delete_prefix("doc")
    second = cached.search([1.0, 0.0], top_k=1)  # still served from cache

    assert first == second and first[0].text == "cached"
