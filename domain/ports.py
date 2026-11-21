# domain/ports.py — 1.4 (LLMPort), 2.4 (EmbeddingPort, VectorStorePort)
#
# Each port asks what the domain actually needs, not what the vendor offers.
from dataclasses import dataclass, field
from typing import Protocol


class LLMPort(Protocol):
    def complete(self, prompt: str) -> str:
        """Return the model's completion for the given prompt."""
        ...


@dataclass
class Match:
    """One result from a vector search, in the domain's terms."""

    id: str
    score: float
    metadata: dict = field(default_factory=dict)


class EmbeddingPort(Protocol):
    def embed(self, text: str) -> list[float]:
        """Return the embedding vector for the given text."""
        ...


class VectorStorePort(Protocol):
    def upsert(self, id: str, vector: list[float], metadata: dict) -> None:
        """Write a vector and its metadata, replacing any existing entry with the same id."""
        ...

    def query(self, vector: list[float], top_k: int) -> list[Match]:
        """Return the top_k nearest matches to the given vector."""
        ...
