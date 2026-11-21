# app/adapters/cached_retriever.py — a RetrievalPort that wraps another one (4.3)
#
# Possible only because the read side has its own port: the composition
# root can put a cache in front of retrieval without AnswerQuestionHandler
# or the write path noticing.
import time

from app.ports import RetrievalPort, RetrievedChunk


class CachedRetriever(RetrievalPort):
    def __init__(self, inner: RetrievalPort, ttl_s: float = 30.0) -> None:
        self._inner = inner
        self._ttl_s = ttl_s
        self._cache: dict[tuple[tuple[float, ...], int], tuple[float, list[RetrievedChunk]]] = {}

    def search(self, embedding: list[float], top_k: int) -> list[RetrievedChunk]:
        key = (tuple(embedding), top_k)
        now = time.monotonic()
        hit = self._cache.get(key)
        if hit is not None and now - hit[0] < self._ttl_s:
            return hit[1]
        results = self._inner.search(embedding, top_k)
        self._cache[key] = (now, results)
        return results
