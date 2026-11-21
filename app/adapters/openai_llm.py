# app/adapters/openai_llm.py — LLMPort implementation (1.4, configured as in 3.4)
from openai import OpenAI

from app.ports import LLMPort


class OpenAILLM(LLMPort):
    def __init__(self, api_key: str, model: str = "gpt-4o", timeout_s: float = 30.0) -> None:
        self._client = OpenAI(api_key=api_key, timeout=timeout_s)
        self._model = model

    def complete(self, prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        return response.choices[0].message.content or ""
