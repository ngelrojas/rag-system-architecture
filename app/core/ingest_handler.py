# app/core/ingest_handler.py — the command handler (3.5's policy, reshaped in 4.4)
from app.core.chunking import split_into_chunks
from app.core.commands import IngestDocumentCommand, IngestResult
from app.ports import EmbeddingPort, VectorStorePort


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
            # Policy (3.5): a document is either fully retrievable or not at all.
            self._vector_store.delete_prefix(prefix=command.doc_id)
            return IngestResult(doc_id=command.doc_id, chunks_ingested=0, succeeded=False)
        return IngestResult(doc_id=command.doc_id, chunks_ingested=len(chunks), succeeded=True)
