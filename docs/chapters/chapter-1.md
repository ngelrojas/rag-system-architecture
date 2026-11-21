# Chapter 1 — The model layer: the first boundary

**Book:** Part I (code in 1.4) · **Branch:** `feature/chapter-1` · **Builds on:** `feature/chapter-0`

| Commit | Section | What changes |
|---|---|---|
| 1 | 1.4 | `naive/answer.py` — the starting point: the vendor call lives inside the answering logic |
| 2 | 1.4 | `domain/ports.py` (`LLMPort`), `adapters/openai_llm.py`, `domain/answering.py`, `tests/fakes.py` (`FakeLLM`) |
| 3 | 1.4 | `.importlinter` — *Domain must not import adapters or vendor SDKs* |

## Layout after this chapter

```
domain/
  ports.py          LLMPort — what the domain needs, in its own terms
  answering.py      answer_question(llm, question, context)
adapters/
  openai_llm.py     OpenAILLM — the only file that knows about OpenAI
naive/answer.py     the "before" version, kept for comparison
tests/
  fakes.py          FakeLLM
  test_answering.py
```

> The book shows the first test inside `tests/fakes.py`. Here it lives in `tests/test_answering.py`, because pytest only collects files named `test_*.py`.

## Try it

```bash
make check
```

Prove the contract: add `from openai import OpenAI` to `domain/answering.py` and run `make boundaries` — the build fails. That failure is the point of 1.4.
