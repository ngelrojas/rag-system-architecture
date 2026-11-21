# app/ports.py — the ports, moved to the edge of the core (3.2)
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
    """In Part III one port serves both writing and searching.
    Part IV (4.3) splits the search side out into RetrievalPort."""

    def upsert(self, key: str, embedding: list[float], metadata: dict) -> None: ...
    def delete_prefix(self, prefix: str) -> None: ...
    def search(self, embedding: list[float], top_k: int) -> list[RetrievedChunk]: ...
