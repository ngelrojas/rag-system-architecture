# services/ingestion.py — 2.4
#
# Something whose entire job is owning what "successfully ingested" means
# for a document, across both calls — including the failure case that used
# to just crash the loop.
from dataclasses import dataclass
from enum import Enum, auto

from domain.ports import EmbeddingPort, VectorStorePort


class ChunkStatus(Enum):
    STORED = auto()
    FAILED = auto()


@dataclass
class ChunkOutcome:
    chunk_id: str
    status: ChunkStatus
    error: str | None = None


class IngestionOrchestrator:
    def __init__(self, embedder: EmbeddingPort, store: VectorStorePort):
        self._embedder = embedder
        self._store = store

    def ingest(self, doc_id: str, chunks: list[str]) -> list[ChunkOutcome]:
        outcomes = []
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}-{i}"
            try:
                vector = self._embedder.embed(chunk)
                self._store.upsert(chunk_id, vector, metadata={"text": chunk})
                outcomes.append(ChunkOutcome(chunk_id, ChunkStatus.STORED))
            except Exception as e:
                outcomes.append(ChunkOutcome(chunk_id, ChunkStatus.FAILED, error=str(e)))
        return outcomes
