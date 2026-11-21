# app/core/document_service.py — the "consolidated" version (4.1)
#
# Ports only. No vendor imports. Looks entirely correct at a glance —
# and still the wrong shape: one model and one port serve two directions
# that change for different reasons. 4.4 takes it apart.
from dataclasses import dataclass

from app.core.chunking import split_into_chunks
from app.ports import EmbeddingPort, LLMPort, VectorStorePort


@dataclass
class Document:
    doc_id: str
    text: str
    chunks: list[str]
    embeddings: list[list[float]]
    metadata: dict


class DocumentService:
    def __init__(self, llm: LLMPort, embedder: EmbeddingPort, vector_store: VectorStorePort):
        self._llm = llm
        self._embedder = embedder
        self._vector_store = vector_store

    def ingest(self, doc_id: str, text: str) -> Document:
        chunks = split_into_chunks(text)
        embeddings = [self._embedder.embed(c) for c in chunks]
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings, strict=True)):
            self._vector_store.upsert(f"{doc_id}-{i}", emb, metadata={"text": chunk})
        return Document(doc_id=doc_id, text=text, chunks=chunks, embeddings=embeddings, metadata={})

    def query(self, question: str) -> str:
        q_embedding = self._embedder.embed(question)
        candidates = self._vector_store.search(q_embedding, top_k=5)
        context = "\n".join(c.text for c in candidates)
        return self._llm.complete(f"Context:\n{context}\n\nQuestion: {question}")
