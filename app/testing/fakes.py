# app/testing/fakes.py — fakes for every port (1.4, 3.4, 3.5, 4.4)
#
# Fakes live inside the app package so tests and demos can import them,
# but app.core never does — the boundary contracts check that.
from app.ports import RetrievedChunk


class FakeLLM:
    def __init__(self, response: str = "fake answer") -> None:
        self._response = response
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self._response


class FakeEmbedder:
    """Deterministic, offline embeddings."""

    def __init__(self) -> None:
        self.calls = 0

    def embed(self, text: str) -> list[float]:
        self.calls += 1
        return [float(len(text)), 1.0]


class FakeVectorStore:
    """Command-side fake: records writes. It has no search — after 4.3 the
    write port doesn't either."""

    def __init__(self) -> None:
        self.rows: dict[str, tuple[list[float], dict]] = {}

    def upsert(self, key: str, embedding: list[float], metadata: dict) -> None:
        self.rows[key] = (embedding, metadata)

    def delete_prefix(self, prefix: str) -> None:
        for key in [k for k in self.rows if k.startswith(prefix)]:
            del self.rows[key]


class FailingAfterNCallsVectorStore(FakeVectorStore):
    """Succeeds for the first `fail_after` upserts, then raises — the seam
    that makes 2.3's partial failure reproducible on purpose (3.5)."""

    def __init__(self, fail_after: int) -> None:
        super().__init__()
        self._fail_after = fail_after
        self.upsert_calls = 0
        self.delete_prefix_called_with: str | None = None

    def upsert(self, key: str, embedding: list[float], metadata: dict) -> None:
        self.upsert_calls += 1
        if self.upsert_calls > self._fail_after:
            raise ConnectionError("vector store unavailable")
        super().upsert(key, embedding, metadata)

    def delete_prefix(self, prefix: str) -> None:
        self.delete_prefix_called_with = prefix
        super().delete_prefix(prefix)


class FakeRetriever:
    """Query-side fake: returns canned chunks. No mutation methods to ignore."""

    def __init__(self, results: list[RetrievedChunk] | None = None) -> None:
        self._results = results or []
        self.calls = 0

    def search(self, embedding: list[float], top_k: int) -> list[RetrievedChunk]:
        self.calls += 1
        return self._results[:top_k]
