# naive/ingest.py — 2.1, the naive pipeline (write path)
from openai import OpenAI

from naive.vector_store import vector_store

client = OpenAI()


def ingest_document(text: str, doc_id: str) -> None:
    chunks = [text[i : i + 500] for i in range(0, len(text), 500)]
    for i, chunk in enumerate(chunks):
        embedding = client.embeddings.create(
            model="text-embedding-3-small",
            input=chunk,
        ).data[0].embedding
        vector_store.upsert(f"{doc_id}-{i}", embedding, metadata={"text": chunk})
