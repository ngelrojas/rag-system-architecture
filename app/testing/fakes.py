# app/testing/fakes.py — fakes for every port (1.4, 3.4, 3.5)
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
    """Stores writes in memory; search returns the canned (text, score) results."""

    def __init__(self, results: list[tuple[str, float]] | None = None) -> None:
        self.rows: dict[str, tuple[list[float], dict]] = {}
        self._results = results or []

    def upsert(self, key: str, embedding: list[float], metadata: dict) -> None:
        self.rows[key] = (embedding, metadata)

    def delete_prefix(self, prefix: str) -> None:
        for key in [k for k in self.rows if k.startswith(prefix)]:
            del self.rows[key]

    def search(self, embedding: list[float], top_k: int) -> list[RetrievedChunk]:
        return [RetrievedChunk(text=t, score=s) for t, s in self._results[:top_k]]
