# app/core/ingest_handler.py — 3.5
#
# The part that resolves 2.3's bug — not by adding error handling to the
# old loop, but by giving the partial-failure decision a home it never had.
from dataclasses import dataclass

from app.core.chunking import split_into_chunks
from app.ports import EmbeddingPort, VectorStorePort


@dataclass
class IngestResult:
    doc_id: str
    chunks_ingested: int
    succeeded: bool


class IngestHandler:
    """
    Domain core. Knows nothing about OpenAI or Qdrant —
    only about EmbeddingPort and VectorStorePort.
    """

    def __init__(self, embedder: EmbeddingPort, vector_store: VectorStorePort, chunk_size: int):
        self._embedder = embedder
        self._vector_store = vector_store
        self._chunk_size = chunk_size

    def handle(self, doc_id: str, text: str) -> IngestResult:
        chunks = split_into_chunks(text, self._chunk_size)

        try:
            for i, chunk in enumerate(chunks):
                embedding = self._embedder.embed(chunk)
                self._vector_store.upsert(
                    key=f"{doc_id}-{i}",
                    embedding=embedding,
                    metadata={"text": chunk},
                )
        except Exception:
            # Policy: a document is either fully retrievable or not
            # retrievable at all. No half-ingested documents survive.
            self._vector_store.delete_prefix(prefix=doc_id)
            return IngestResult(doc_id=doc_id, chunks_ingested=0, succeeded=False)

        return IngestResult(doc_id=doc_id, chunks_ingested=len(chunks), succeeded=True)
