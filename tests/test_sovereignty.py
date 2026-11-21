# tests/test_sovereignty.py — 6.6
import httpx
import pytest

from app.adapters.local_embeddings import LocalEmbeddings
from app.composition import build_application
from app.config import Settings


def test_local_embeddings_never_call_out() -> None:
    def private_server(request: httpx.Request) -> httpx.Response:
        assert request.url.host == "embed.internal"
        return httpx.Response(200, json={"data": [{"embedding": [0.1, 0.2, 0.3]}]})

    client = httpx.Client(base_url="http://embed.internal", transport=httpx.MockTransport(private_server))
    assert LocalEmbeddings("http://embed.internal", "nomic-embed-text", client=client).embed("text") == [0.1, 0.2, 0.3]


def test_sovereign_mode_needs_no_cloud_credentials() -> None:
    settings = Settings(deployment_mode="sovereign", openai_api_key="", private_qdrant_url=":memory:")
    assert build_application(settings).ingest_handler is not None


def test_unknown_deployment_mode_fails_fast() -> None:
    with pytest.raises(ValueError):
        build_application(Settings(deployment_mode="hybrid", qdrant_url=":memory:"))
