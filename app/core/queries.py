# app/core/queries.py — the read side's model (4.2, after the 4.4 refactor)
from dataclasses import dataclass


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
