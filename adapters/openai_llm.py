# adapters/openai_llm.py — 1.4
#
# All the vendor knowledge goes here, to be contained.
from openai import OpenAI


class OpenAILLM:
    def __init__(self, client: OpenAI, model: str = "gpt-4o") -> None:
        self._client = client
        self._model = model

    def complete(self, prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        return response.choices[0].message.content or ""
