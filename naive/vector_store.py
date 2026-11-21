# naive/vector_store.py — a stand-in for "the vector store client that was in scope"
#
# The naive pipeline in 2.1 uses a module-level vector_store without saying
# where it comes from. This tiny in-memory version makes the naive code run.
import math
from dataclasses import dataclass, field


@dataclass
class Match:
    id: str
    score: float
    metadata: dict = field(default_factory=dict)


class InMemoryVectorStore:
    def __init__(self) -> None:
        self._rows: dict[str, tuple[list[float], dict]] = {}

    def upsert(self, id: str, vector: list[float], metadata: dict) -> None:
        self._rows[id] = (vector, metadata)

    def query(self, vector: list[float], top_k: int) -> list[Match]:
        def cosine(a: list[float], b: list[float]) -> float:
            dot = sum(x * y for x, y in zip(a, b, strict=False))
            na = math.sqrt(sum(x * x for x in a)) or 1.0
            nb = math.sqrt(sum(y * y for y in b)) or 1.0
            return dot / (na * nb)

        scored = [Match(i, cosine(vector, v), m) for i, (v, m) in self._rows.items()]
        return sorted(scored, key=lambda m: m.score, reverse=True)[:top_k]


vector_store = InMemoryVectorStore()
