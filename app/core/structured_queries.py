# app/core/structured_queries.py — the structured read model (5.5)
from dataclasses import dataclass, field


@dataclass
class StructuredQuery:
    question: str


@dataclass
class StructuredAnswer:
    answer: str
    sql: str
    rows: list[dict] = field(default_factory=list)
