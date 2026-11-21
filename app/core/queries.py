# app/core/queries.py — the read side. A completely different model. (4.2)
from dataclasses import dataclass

from app.ports import EmbeddingPort, LLMPort, VectorStorePort


@dataclass
class AnswerQuestionQuery:
    question: str
    min_relevance: float


@dataclass
class AnsweredQuestion:
    answer: str
    chunks_used: list[str]
    # No doc_id, no chunk_size, nothing about how the data got written.
    # Only what a reader needs to see.


class AnswerQuestionHandler:
    def __init__(self, llm: LLMPort, embedder: EmbeddingPort, vector_store: VectorStorePort):
        self._llm = llm
        self._embedder = embedder
        self._vector_store = vector_store

    def handle(self, query: AnswerQuestionQuery) -> AnsweredQuestion:
        q_embedding = self._embedder.embed(query.question)
        candidates = self._vector_store.search(q_embedding, top_k=5)
        relevant = [c for c in candidates if c.score >= query.min_relevance]
        context = "\n".join(c.text for c in relevant)
        answer = self._llm.complete(f"Context:\n{context}\n\nQuestion: {query.question}")
        return AnsweredQuestion(answer=answer, chunks_used=[c.text for c in relevant])
