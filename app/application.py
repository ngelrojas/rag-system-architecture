# app/application.py — the shape of a fully wired application
#
# Lives in its own module so driving adapters (HTTP, CLI) can depend on the
# *shape* of what the composition root builds without importing the
# composition root — and with it, every concrete adapter.
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from app.core.ingest_handler import IngestDocumentHandler
from app.core.query_budget import QueryBudget
from app.core.query_handler import AnswerQuestionHandler
from app.core.structured_query_handler import StructuredQueryHandler
from app.ports import LLMPort


@dataclass
class Application:
    """Everything the driving adapters need, fully wired."""

    query_handler: AnswerQuestionHandler
    ingest_handler: IngestDocumentHandler
    structured_handler: StructuredQueryHandler
    answer_graph: Any
    review_graph: Any
    multi_agent_graph: Any
    min_relevance: float
    judge_llm: LLMPort
    judge_sample_rate: float
    max_llm_calls_per_request: int
    # 6.2 / 6.5 — request-scoped construction: ports wrapped with one trace_id and one budget
    make_query_handler: Callable[[str, QueryBudget], AnswerQuestionHandler]
    make_answer_graph: Callable[[str, QueryBudget], Any]
