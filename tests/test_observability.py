# tests/test_observability.py — 6.2, reconstructing a request from its spans
from structlog.testing import capture_logs

from app.composition import build_request_scoped_ports
from app.core.queries import AnswerQuestionQuery
from app.core.query_handler import AnswerQuestionHandler
from app.ports import RetrievedChunk
from app.testing.fakes import FakeEmbedder, FakeLLM, FakeRetriever


def test_every_port_call_logs_a_span_under_one_trace_id() -> None:
    llm, embedder, retriever = build_request_scoped_ports(
        FakeLLM("answer"), FakeEmbedder(), FakeRetriever([RetrievedChunk("chunk", 0.41)]), trace_id="9f2a"
    )
    handler = AnswerQuestionHandler(llm=llm, embedder=embedder, retriever=retriever)

    with capture_logs() as logs:
        handler.handle(AnswerQuestionQuery(question="why?", min_relevance=0.3))

    ends = [e for e in logs if e["event"] == "port_call_end"]
    assert [e["port"] for e in ends] == ["EmbeddingPort", "RetrievalPort", "LLMPort"]
    assert {e["trace_id"] for e in logs} == {"9f2a"}
    provenance = next(e for e in logs if e["event"] == "retrieval_results")
    assert provenance["top_score"] == 0.41  # the 6.2 example: a weak top score explains a weak answer


def test_errors_are_logged_and_re_raised() -> None:
    class Broken:
        def complete(self, prompt: str) -> str:
            raise TimeoutError("provider down")

    llm, _, _ = build_request_scoped_ports(Broken(), FakeEmbedder(), FakeRetriever(), trace_id="t1")
    with capture_logs() as logs:
        try:
            llm.complete("x")
        except TimeoutError:
            pass
    assert logs[-1]["status"] == "error" and logs[-1]["error"] == "provider down"
