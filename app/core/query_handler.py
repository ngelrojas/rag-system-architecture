# app/core/query_handler.py — 3.3 policy, wired in 3.4
#
# What belongs in the core is not the similarity math (that's the vector
# store's job) but the policy decisions 3.3 names: how relevant is relevant
# enough, and whether to answer at all when nothing clears the bar.
from dataclasses import dataclass

from app.ports import EmbeddingPort, LLMPort, VectorStorePort

NO_GROUNDED_ANSWER = "I couldn't find anything in the documents that answers this question."


@dataclass
class QueryResult:
    answer: str
    chunks_used: list[str]


class QueryHandler:
    def __init__(
        self,
        llm: LLMPort,
        embedder: EmbeddingPort,
        vector_store: VectorStorePort,
        min_relevance: float,
        top_k: int = 5,
    ) -> None:
        self._llm = llm
        self._embedder = embedder
        self._vector_store = vector_store
        self._min_relevance = min_relevance
        self._top_k = top_k

    def handle(self, question: str) -> QueryResult:
        q_embedding = self._embedder.embed(question)
        candidates = self._vector_store.search(q_embedding, top_k=self._top_k)

        # Policy 1 (3.3): below the threshold, a candidate is noise, not context.
        relevant = [c for c in candidates if c.score >= self._min_relevance]

        # Policy 2 (3.3): refuse rather than let the model answer from nothing.
        if not relevant:
            return QueryResult(answer=NO_GROUNDED_ANSWER, chunks_used=[])

        context = "\n".join(c.text for c in relevant)
        answer = self._llm.complete(f"Context:\n{context}\n\nQuestion: {question}")
        return QueryResult(answer=answer, chunks_used=[c.text for c in relevant])
