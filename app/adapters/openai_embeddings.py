# app/adapters/openai_embeddings.py — EmbeddingPort implementation (3.5)
from openai import OpenAI

from app.ports import EmbeddingPort


class OpenAIEmbeddings(EmbeddingPort):
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def embed(self, text: str) -> list[float]:
        response = self._client.embeddings.create(model=self._model, input=text)
        return list(response.data[0].embedding)
