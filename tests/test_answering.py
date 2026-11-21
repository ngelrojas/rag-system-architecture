# tests/test_answering.py — 1.4
from domain.answering import answer_question
from domain.ports import LLMPort
from tests.fakes import FakeLLM


def test_context_reaches_the_model() -> None:
    llm = FakeLLM(canned="Paris.")
    answer = answer_question(llm, "Capital of France?", ["France's capital is Paris."])
    assert answer == "Paris."
    assert "France's capital is Paris." in llm.prompts[0]


def test_fake_and_adapter_satisfy_the_same_port() -> None:
    # mypy checks these assignments statically: both shapes must match LLMPort.
    from openai import OpenAI

    from adapters.openai_llm import OpenAILLM

    real: LLMPort = OpenAILLM(OpenAI(api_key="sk-test-not-used"))
    fake: LLMPort = FakeLLM(canned="ok")
    assert real is not None
    assert fake.complete("anything") == "ok"
