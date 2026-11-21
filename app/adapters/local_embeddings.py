# app/adapters/local_embeddings.py — 6.6
#
# The second, separate egress point: if embeddings still go to a cloud
# API, document text leaves the network even when inference doesn't.
import httpx

from app.ports import EmbeddingPort


class LocalEmbeddings(EmbeddingPort):
    """Embeds via a locally-hosted embedding model. No text ever
    leaves the private network to compute a vector."""

    def __init__(self, base_url: str, model: str, client: httpx.Client | None = None):
        self._client = client or httpx.Client(base_url=base_url, timeout=60.0)
        self._model = model

    def embed(self, text: str) -> list[float]:
        response = self._client.post("/v1/embeddings", json={"model": self._model, "input": text})
        response.raise_for_status()
        return [float(x) for x in response.json()["data"][0]["embedding"]]
