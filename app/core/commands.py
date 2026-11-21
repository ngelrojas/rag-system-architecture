# app/core/commands.py — the write side. Owns its own model. (4.2)
from dataclasses import dataclass

from app.core.chunking import split_into_chunks
from app.ports import EmbeddingPort, VectorStorePort


@dataclass
class IngestDocumentCommand:
    doc_id: str
    text: str


@dataclass
class IngestResult:
    doc_id: str
    chunks_ingested: int
    succeeded: bool
    # No answer data, no candidates, no chunks returned.
    # Only confirmation that the write happened.


class IngestDocumentHandler:
    def __init__(self, embedder: EmbeddingPort, vector_store: VectorStorePort, chunk_size: int):
        self._embedder = embedder
        self._vector_store = vector_store
        self._chunk_size = chunk_size

    def handle(self, command: IngestDocumentCommand) -> IngestResult:
        chunks = split_into_chunks(command.text, self._chunk_size)
        try:
            for i, chunk in enumerate(chunks):
                embedding = self._embedder.embed(chunk)
                self._vector_store.upsert(
                    key=f"{command.doc_id}-{i}", embedding=embedding, metadata={"text": chunk},
                )
        except Exception:
            self._vector_store.delete_prefix(prefix=command.doc_id)
            return IngestResult(doc_id=command.doc_id, chunks_ingested=0, succeeded=False)
        return IngestResult(doc_id=command.doc_id, chunks_ingested=len(chunks), succeeded=True)
