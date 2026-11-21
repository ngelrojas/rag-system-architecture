# tests/test_qdrant_store.py — the real adapter, against in-process Qdrant
from app.adapters.qdrant_store import QdrantVectorStore
from app.ports import VectorStorePort


def make_store() -> VectorStorePort:
    return QdrantVectorStore(url=":memory:", collection="chunks")


def test_upsert_then_search_round_trip() -> None:
    store = make_store()
    store.upsert("doc-0", [1.0, 0.0], {"text": "about cats"})
    store.upsert("doc-1", [0.0, 1.0], {"text": "about dogs"})

    results = store.search([0.9, 0.1], top_k=1)

    assert results[0].text == "about cats"
    assert results[0].score > 0.9


def test_delete_prefix_removes_a_whole_document() -> None:
    store = make_store()
    for i in range(3):
        store.upsert(f"policy-{i}", [1.0, float(i)], {"text": f"policy part {i}"})
    store.upsert("other-0", [1.0, 0.0], {"text": "unrelated"})

    store.delete_prefix("policy")

    assert [r.text for r in store.search([1.0, 0.0], top_k=10)] == ["unrelated"]
