# domain/ports.py — 1.4
#
# A port is defined by what the domain needs, in the domain's own terms —
# not by what the vendor offers.
from typing import Protocol


class LLMPort(Protocol):
    def complete(self, prompt: str) -> str:
        """Return the model's completion for the given prompt."""
        ...
