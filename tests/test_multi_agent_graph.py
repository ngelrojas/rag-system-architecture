# tests/test_multi_agent_graph.py — 5.5, routing and synthesis behind clean ports
from typing import Any

from app.adapters.orchestration.multi_agent_graph import build_multi_agent_graph
from app.core.query_handler import AnswerQuestionHandler
from app.core.structured_query_handler import StructuredQueryHandler
from app.ports import RetrievedChunk
from app.testing.fakes import FakeEmbedder, FakeLLM, FakeRetriever, FakeStructuredQueryPort, ScriptedLLM


def make_graph(router_llm: ScriptedLLM) -> Any:
    answer = AnswerQuestionHandler(
        llm=FakeLLM("from documents"), embedder=FakeEmbedder(), retriever=FakeRetriever([RetrievedChunk("doc", 0.9)])
    )
    structured = StructuredQueryHandler(
        llm=ScriptedLLM(["SELECT 1", "from database"]), db=FakeStructuredQueryPort([{"n": 1}]), schema=""
    )
    return build_multi_agent_graph(answer, structured, router_llm)


def test_semantic_route_uses_only_document_search() -> None:
    state = make_graph(ScriptedLLM(["document search"])).invoke({"question": "what does the policy say?"})
    assert state["route"] == "semantic"
    assert state["final_answer"] == "from documents"


def test_structured_route_uses_only_the_database() -> None:
    state = make_graph(ScriptedLLM(["a database count"])).invoke({"question": "how many policies?"})
    assert state["route"] == "structured"
    assert state["final_answer"] == "from database"


def test_both_routes_run_and_are_synthesized() -> None:
    router = ScriptedLLM(["both", "combined answer"])
    state = make_graph(router).invoke({"question": "how many policies changed, and how?"})
    assert state["route"] == "both"
    assert state["final_answer"] == "combined answer"
    assert "from documents" in router.prompts[1] and "from database" in router.prompts[1]
