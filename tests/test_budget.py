# tests/test_budget.py — 6.5, cost as an architectural constraint
import pytest
from fastapi.testclient import TestClient
from langgraph.checkpoint.memory import InMemorySaver

from app.adapters.api.http_handler import create_api
from app.composition import wire
from app.config import Settings
from app.core.query_budget import BudgetExceededError, QueryBudget
from app.observability.budgeted_llm import BudgetedLLMPort
from app.ports import RetrievedChunk
from app.testing.fakes import FakeEmbedder, FakeLLM, FakeRetriever, FakeStructuredQueryPort, FakeVectorStore


def test_the_call_over_budget_never_reaches_the_model() -> None:
    model = FakeLLM()
    llm = BudgetedLLMPort(model, QueryBudget(max_llm_calls=2))
    llm.complete("1")
    llm.complete("2")
    with pytest.raises(BudgetExceededError):
        llm.complete("3")
    assert model.prompts == ["1", "2"]


def make_client(max_calls: int, retriever: FakeRetriever) -> TestClient:
    settings = Settings(max_llm_calls_per_request=max_calls)
    ports = (FakeLLM("no"), FakeEmbedder(), FakeVectorStore(), retriever, FakeStructuredQueryPort())
    application = wire(settings, *ports, InMemorySaver())
    return TestClient(create_api(application))


def test_a_retrying_graph_stops_at_the_budget_with_429() -> None:
    # Nothing relevant, so the handler refuses without calling the model. The graph still
    # calls the LLM to classify (call 1) and to reformulate before retrying (call 2 — over budget).
    response = make_client(max_calls=1, retriever=FakeRetriever([RetrievedChunk("weak", 0.1)])).post(
        "/ask", json={"text": "unknowable"}
    )
    assert response.status_code == 429
    assert response.json()["error"] == "budget_exceeded"


def test_each_request_gets_a_fresh_budget() -> None:
    client = make_client(max_calls=1, retriever=FakeRetriever([RetrievedChunk("policy", 0.9)]))
    for _ in range(3):
        assert client.post("/query", json={"text": "q"}).status_code == 200
