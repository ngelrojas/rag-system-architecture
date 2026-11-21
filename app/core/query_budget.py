# app/core/query_budget.py — 6.5
#
# A policy object, not infrastructure. Decides how many LLM calls a
# single logical request is allowed to make before it must stop —
# a domain-level decision about acceptable cost, the same category
# of decision as 3.3's relevance threshold.
from dataclasses import dataclass, field


class BudgetExceededError(Exception):
    pass


@dataclass
class QueryBudget:
    max_llm_calls: int = 3
    calls_made: int = field(default=0, init=False)

    def record_call(self) -> None:
        self.calls_made += 1
        if self.calls_made > self.max_llm_calls:
            raise BudgetExceededError(f"Query exceeded budget of {self.max_llm_calls} LLM calls")
