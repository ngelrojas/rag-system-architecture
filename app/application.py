# app/application.py — the shape of a fully wired application
#
# Lives in its own module so driving adapters (HTTP, CLI) can depend on the
# *shape* of what the composition root builds without importing the
# composition root — and with it, every concrete adapter.
from dataclasses import dataclass
from typing import Any

from app.core.ingest_handler import IngestDocumentHandler
from app.core.query_handler import AnswerQuestionHandler


@dataclass
class Application:
    """Everything the driving adapters need, fully wired."""

    query_handler: AnswerQuestionHandler
    ingest_handler: IngestDocumentHandler
    answer_graph: Any
    review_graph: Any
    min_relevance: float
