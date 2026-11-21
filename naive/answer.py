# naive/answer.py — 1.4, the starting point
#
# Somewhere deep in the answering logic: the vendor SDK, the model name and
# the decoding settings are welded into the function that decides how to
# answer. Deleting the vendor means deleting the answering logic.
from openai import OpenAI

client = OpenAI()


def answer_question(question: str, context: list[str]) -> str:
    prompt = f"Context:\n{chr(10).join(context)}\n\nQuestion: {question}"
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
    )
    return response.choices[0].message.content or ""
