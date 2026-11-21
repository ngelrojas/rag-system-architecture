# app/core/query_handler.py — the query handler (4.3, 4.4)
#
# Depends on RetrievalPort, not VectorStorePort: the read side cannot
# mutate the store, and the composition root can point it at a replica
# or a cache without this file changing.
from app.core.queries import AnsweredQuestion, AnswerQuestionQuery
from app.ports import EmbeddingPort, LLMPort, RetrievalPort

# 3.3's grounding policy, carried over: refuse rather than answer from nothing.
NO_GROUNDED_ANSWER = "I couldn't find anything in the documents that answers this question."


class AnswerQuestionHandler:
    def __init__(self, llm: LLMPort, embedder: EmbeddingPort, retriever: RetrievalPort):
        self._llm = llm
        self._embedder = embedder
        self._retriever = retriever  # was vector_store: VectorStorePort

    def handle(self, query: AnswerQuestionQuery) -> AnsweredQuestion:
        q_embedding = self._embedder.embed(query.question)
        candidates = self._retriever.search(q_embedding, top_k=5)
        relevant = [c for c in candidates if c.score >= query.min_relevance]
        if not relevant:
            return AnsweredQuestion(answer=NO_GROUNDED_ANSWER, chunks_used=[])
        context = "\n".join(c.text for c in relevant)
        answer = self._llm.complete(f"Context:\n{context}\n\nQuestion: {query.question}")
        return AnsweredQuestion(answer=answer, chunks_used=[c.text for c in relevant])
