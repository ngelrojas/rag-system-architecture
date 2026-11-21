# tests/test_local_inference.py — 6.4, same contract, private infrastructure
import json

import httpx
import pytest

from app.adapters.local_llm import LocalLLM
from app.composition import build_application
from app.config import Settings
from app.ports import LLMPort


def test_local_llm_speaks_the_openai_compatible_protocol() -> None:
    def server(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        assert request.url.path == "/v1/chat/completions"
        assert body["model"] == "qwen2.5:7b"
        return httpx.Response(200, json={"choices": [{"message": {"content": "local answer"}}]})

    client = httpx.Client(base_url="http://local", transport=httpx.MockTransport(server))
    llm: LLMPort = LocalLLM(base_url="http://local", model="qwen2.5:7b", client=client)
    assert llm.complete("hello") == "local answer"


def test_the_swap_is_a_composition_root_decision() -> None:
    # Only the LLM is swapped here; embeddings still go to OpenAI until 6.6.
    settings = Settings(inference_mode="local", openai_api_key="sk-embeddings-only", qdrant_url=":memory:")
    assert build_application(settings).query_handler is not None


def test_unknown_inference_mode_fails_fast() -> None:
    with pytest.raises(ValueError):
        build_application(Settings(inference_mode="quantum", openai_api_key="sk-x", qdrant_url=":memory:"))
