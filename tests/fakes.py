# tests/fakes.py — 1.4
#
# The proof that LLMPort is a real port: something else can play the role
# without the domain noticing.


class FakeLLM:
    def __init__(self, canned: str) -> None:
        self._canned = canned
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self._canned
