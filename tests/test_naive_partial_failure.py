# tests/test_naive_partial_failure.py — 2.3, the bug that needs a second wrapper
#
# This test documents a failure instead of preventing one: when the third
# embedding call fails, the naive loop has already stored the first two
# chunks. The document is now half-ingested and nothing in the code owns
# that outcome. Part II's orchestrator (2.4) and Part III's rollback policy
# (3.5) are the answers.
import os
from types import SimpleNamespace

import pytest

os.environ.setdefault("OPENAI_API_KEY", "sk-test-not-used")  # the naive module builds a client at import

from naive import ingest as naive_ingest  # noqa: E402
from naive.vector_store import InMemoryVectorStore  # noqa: E402


class FlakyEmbeddings:
    def __init__(self, fail_on_call: int) -> None:
        self.calls = 0
        self.fail_on_call = fail_on_call

    def create(self, model: str, input: str) -> SimpleNamespace:
        self.calls += 1
        if self.calls == self.fail_on_call:
            raise TimeoutError("embedding provider timed out")
        return SimpleNamespace(data=[SimpleNamespace(embedding=[1.0, 0.0])])


def test_naive_ingestion_leaves_a_half_ingested_document(monkeypatch: pytest.MonkeyPatch) -> None:
    store = InMemoryVectorStore()
    monkeypatch.setattr(naive_ingest, "vector_store", store)
    monkeypatch.setattr(naive_ingest, "client", SimpleNamespace(embeddings=FlakyEmbeddings(fail_on_call=3)))

    with pytest.raises(TimeoutError):
        naive_ingest.ingest_document("x" * 2000, doc_id="policy")  # four chunks

    # Two chunks survived. Retrieval will now answer from half a document.
    assert len(store.query([1.0, 0.0], top_k=10)) == 2
