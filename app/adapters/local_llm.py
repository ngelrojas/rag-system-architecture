# app/adapters/local_llm.py — 6.4
#
# Runs inference against a locally-hosted model — DeepSeek, Qwen, or
# any model served through an OpenAI-compatible local inference server
# (vLLM, Ollama, llama.cpp server, etc). Satisfies LLMPort exactly.
import httpx

from app.ports import LLMPort


class LocalLLM(LLMPort):
    """
    Talks to a local inference server over HTTP, on private infrastructure.
    No API key leaves the network. No per-token billing. No dependency
    on an external provider's uptime.
    """

    def __init__(self, base_url: str, model: str, timeout_s: float = 60.0, client: httpx.Client | None = None):
        self._client = client or httpx.Client(base_url=base_url, timeout=timeout_s)
        self._model = model

    def complete(self, prompt: str) -> str:
        response = self._client.post(
            "/v1/chat/completions",
            json={
                "model": self._model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0,
            },
        )
        response.raise_for_status()
        return str(response.json()["choices"][0]["message"]["content"])
