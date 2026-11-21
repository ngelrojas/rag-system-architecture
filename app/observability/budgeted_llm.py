# app/observability/budgeted_llm.py — 6.5
#
# Same composition pattern as TracedLLMPort and PiiGuardrailLLM —
# wraps any LLMPort, enforces the budget before the call proceeds.
from app.core.query_budget import QueryBudget
from app.ports import LLMPort


class BudgetedLLMPort(LLMPort):
    def __init__(self, inner: LLMPort, budget: QueryBudget):
        self._inner = inner
        self._budget = budget

    def complete(self, prompt: str) -> str:
        self._budget.record_call()  # raises if this call would exceed budget
        return self._inner.complete(prompt)
