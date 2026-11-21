# tests/fakes.py — 1.4 (FakeLLM), 2.4 (FakeEmbedder, FakeVectorStore)
from domain.ports import Match


class FakeLLM:
    def __init__(self, canned: str) -> None:
        self._canned = canned
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self._canned


class FakeEmbedder:
    """Deterministic, offline embeddings. Can be told to fail on the Nth call."""

    def __init__(self, fail_on_call: int | None = None) -> None:
        self.calls = 0
        self._fail_on_call = fail_on_call

    def embed(self, text: str) -> list[float]:
        self.calls += 1
        if self._fail_on_call is not None and self.calls == self._fail_on_call:
            raise TimeoutError("embedding provider timed out")
        return [float(len(text)), 1.0]


class FakeVectorStore:
    def __init__(self, matches: list[Match] | None = None) -> None:
        self.rows: dict[str, tuple[list[float], dict]] = {}
        self._matches = matches or []

    def upsert(self, id: str, vector: list[float], metadata: dict) -> None:
        self.rows[id] = (vector, metadata)

    def query(self, vector: list[float], top_k: int) -> list[Match]:
        return self._matches[:top_k]
