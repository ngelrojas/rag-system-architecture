# naive/query.py — 2.1, the naive pipeline (read path)
from naive.ingest import client
from naive.vector_store import vector_store


def answer(question: str) -> str:
    query_embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=question,
    ).data[0].embedding

    matches = vector_store.query(query_embedding, top_k=4)
    context = [m.metadata["text"] for m in matches]

    prompt = f"Context:\n{chr(10).join(context)}\n\nQuestion: {question}"
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content or ""
