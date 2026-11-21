# adapters/openai_embeddings.py — 2.4
from openai import OpenAI


class OpenAIEmbeddings:
    def __init__(self, client: OpenAI, model: str = "text-embedding-3-small") -> None:
        self._client = client
        self._model = model

    def embed(self, text: str) -> list[float]:
        response = self._client.embeddings.create(model=self._model, input=text)
        return list(response.data[0].embedding)
