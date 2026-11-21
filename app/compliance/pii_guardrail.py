# app/compliance/pii_guardrail.py — 6.3
#
# Not about blocking a dangerous action — about blocking sensitive data
# from crossing a boundary it shouldn't: the model never sees it.
import re

from app.ports import LLMPort

SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
CPF_PATTERN = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")  # Brazil's CPF, for LGPD
EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")


class PiiGuardrailLLM(LLMPort):
    """Wraps any LLMPort. Scans the context passed into the prompt for
    PII patterns and redacts them before the call reaches the model —
    the model never sees the raw sensitive data at all."""

    def __init__(self, inner: LLMPort):
        self._inner = inner

    def complete(self, prompt: str) -> str:
        redacted = SSN_PATTERN.sub("[REDACTED-SSN]", prompt)
        redacted = CPF_PATTERN.sub("[REDACTED-CPF]", redacted)
        redacted = EMAIL_PATTERN.sub("[REDACTED-EMAIL]", redacted)
        return self._inner.complete(redacted)
