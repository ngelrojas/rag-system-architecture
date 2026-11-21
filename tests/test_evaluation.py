# tests/test_evaluation.py — 6.1
from app.core.queries import AnsweredQuestion, AnswerQuestionQuery
from app.evaluation.deterministic_checks import run_deterministic_checks
from app.evaluation.llm_judge import judge_answer_quality
from app.testing.fakes import FakeLLM


def test_grounded_answer_passes() -> None:
    check = run_deterministic_checks(AnsweredQuestion(answer="Economy class.", chunks_used=["policy"]))
    assert check.passed and check.failures == []


def test_answer_without_citations_is_flagged() -> None:
    check = run_deterministic_checks(AnsweredQuestion(answer="Probably economy.", chunks_used=[]))
    assert check.failures == ["answer_without_citations"]


def test_empty_and_long_answers_are_flagged() -> None:
    assert "empty_answer" in run_deterministic_checks(AnsweredQuestion(answer=" ", chunks_used=["x"])).failures
    long = AnsweredQuestion(answer="x" * 4001, chunks_used=["x"])
    assert "answer_suspiciously_long" in run_deterministic_checks(long).failures


def test_judge_goes_through_llm_port_and_parses_a_score() -> None:
    judge = FakeLLM(response="4 - addresses the question using only the sources.")
    verdict = judge_answer_quality(
        AnswerQuestionQuery(question="q", min_relevance=0.5), AnsweredQuestion("a", ["s"]), judge
    )
    assert verdict["score"] == 4
    assert "Sources used: ['s']" in judge.prompts[0]
