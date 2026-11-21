# examples/idiomatic_langgraph.py — 5.2, the idiomatic version
#
# Written the way most LangGraph tutorials show it. Read this as "how the
# library wants to be used," not as a recommendation: every node reaches
# for a concrete client that happens to be in scope. 5.3 rebuilds the same
# behavior as a driving adapter in app/adapters/orchestration/answer_graph.py.
#
#   uv run python -m examples.idiomatic_langgraph   (needs OPENAI_API_KEY and Qdrant)
import os
from typing import TypedDict

from langgraph.graph import END, StateGraph
from openai import OpenAI
from qdrant_client import QdrantClient

openai_client = OpenAI()
qdrant_client = QdrantClient(location=os.environ.get("QDRANT_URL", "http://localhost:6333"))


class GraphState(TypedDict, total=False):
    question: str
    candidates: list[str]
    grade: str
    answer: str


def retrieve_node(state: GraphState) -> dict:
    # Direct call to a concrete embedding client and vector store —
    # not a port, not an adapter, just whatever's in scope.
    embedding = openai_client.embeddings.create(input=state["question"], model="text-embedding-3-small")
    results = qdrant_client.query_points(
        collection_name="chunks", query=embedding.data[0].embedding, limit=5, with_payload=True
    ).points
    return {"candidates": [str((r.payload or {}).get("text", "")) for r in results]}


def grade_node(state: GraphState) -> dict:
    # Direct call to the LLM, to judge the LLM's own future input
    prompt = f"Do these passages answer the question '{state['question']}'? {state['candidates']}"
    verdict = openai_client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
    content = (verdict.choices[0].message.content or "").lower()
    return {"grade": "sufficient" if "yes" in content else "insufficient"}


def generate_node(state: GraphState) -> dict:
    prompt = f"Context: {state['candidates']}\n\nQuestion: {state['question']}"
    response = openai_client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
    return {"answer": response.choices[0].message.content or ""}


def route_after_grading(state: GraphState) -> str:
    return "generate" if state["grade"] == "sufficient" else "retrieve"


graph = StateGraph(GraphState)
graph.add_node("retrieve", retrieve_node)
graph.add_node("grade", grade_node)
graph.add_node("generate", generate_node)
graph.set_entry_point("retrieve")
graph.add_edge("retrieve", "grade")
graph.add_conditional_edges("grade", route_after_grading, {"generate": "generate", "retrieve": "retrieve"})
graph.add_edge("generate", END)

app = graph.compile()

if __name__ == "__main__":
    result = app.invoke({"question": "compare the 2022 and 2023 policy documents"})
    print(result["answer"])
