# app/evaluation/llm_judge.py — 6.1, the middle of the pyramid
#
# Sampled, not universal. Uses LLMPort — the same port from Part I —
# because judging IS an LLM call, just a different one than answering.
import re

from app.core.queries import AnsweredQuestion, AnswerQuestionQuery
from app.ports import LLMPort


def judge_answer_quality(query: AnswerQuestionQuery, result: AnsweredQuestion, judge_llm: LLMPort) -> dict:
    prompt = f"""Question: {query.question}
Answer: {result.answer}
Sources used: {result.chunks_used}
Rate 1-5: does the answer directly address the question using ONLY the
sources provided, without adding unsupported claims? Respond with just
the number and one sentence of reasoning."""
    verdict = judge_llm.complete(prompt)
    match = re.search(r"[1-5]", verdict)
    return {"raw_verdict": verdict, "score": int(match.group()) if match else None}
