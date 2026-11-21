# app/evaluation/deterministic_checks.py — 6.1, the base of the pyramid
#
# Runs on every AnswerQuestionHandler.handle() call. No LLM call, no
# sampling — this layer's entire value is that it's cheap enough to
# run 100% of the time.
from dataclasses import dataclass

from app.core.queries import AnsweredQuestion


@dataclass
class DeterministicCheckResult:
    passed: bool
    failures: list[str]


def run_deterministic_checks(result: AnsweredQuestion) -> DeterministicCheckResult:
    failures = []
    if not result.answer.strip():
        failures.append("empty_answer")
    if not result.chunks_used:
        # 3.3's grounding policy said: don't answer from nothing.
        # This check verifies that policy actually held, mechanically.
        failures.append("answer_without_citations")
    if len(result.answer) > 4000:
        failures.append("answer_suspiciously_long")
    return DeterministicCheckResult(passed=not failures, failures=failures)
