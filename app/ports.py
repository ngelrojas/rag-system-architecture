# app/ports.py — Part III's ports, extended with a read-shaped one (4.3)
#
# Ports are defined by the core, in the core's terms. Adapters implement
# them; the core only ever sees these Protocols.
from dataclasses import dataclass
from typing import Protocol


class LLMPort(Protocol):
    def complete(self, prompt: str) -> str:
        """Return the model's completion for the given prompt."""
        ...


class EmbeddingPort(Protocol):
    def embed(self, text: str) -> list[float]:
        """Return the embedding vector for the given text."""
        ...


@dataclass
class RetrievedChunk:
    text: str
    score: float


class VectorStorePort(Protocol):
    """Command-side port. Strict, consistent, owned by IngestDocumentHandler."""

    def upsert(self, key: str, embedding: list[float], metadata: dict) -> None: ...
    def delete_prefix(self, prefix: str) -> None: ...


class RetrievalPort(Protocol):
    """Query-side port. Shaped entirely around answering: given a vector,
    return scored candidates. No mutation methods exist on this port at all —
    the type itself makes misuse from the query side impossible."""

    def search(self, embedding: list[float], top_k: int) -> list[RetrievedChunk]: ...
