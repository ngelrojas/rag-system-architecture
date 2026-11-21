# domain/answering.py — 1.4
#
# The domain logic loses its vendor knowledge entirely.
from domain.ports import LLMPort


def answer_question(llm: LLMPort, question: str, context: list[str]) -> str:
    prompt = f"Context:\n{chr(10).join(context)}\n\nQuestion: {question}"
    return llm.complete(prompt)
