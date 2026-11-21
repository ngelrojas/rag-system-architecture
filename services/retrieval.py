# services/retrieval.py — 2.4, the same move on the query side
from domain.ports import EmbeddingPort, VectorStorePort


class RetrievalOrchestrator:
    def __init__(self, embedder: EmbeddingPort, store: VectorStorePort):
        self._embedder = embedder
        self._store = store

    def retrieve(self, question: str, top_k: int = 4) -> list[str]:
        query_vector = self._embedder.embed(question)
        matches = self._store.query(query_vector, top_k=top_k)
        return [m.metadata["text"] for m in matches]
