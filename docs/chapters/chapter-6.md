# Chapter 6 — Cross-cutting concerns

**Book:** Part VI · **Branch:** `feature/chapter-6` · **Builds on:** `feature/chapter-5`

Every concern in this chapter uses the same move: **wrap a port, once, in the composition root**. No handler and no graph changes.

| Commit | Section | What changes |
|---|---|---|
| 1 | 6.1 | `app/evaluation/` — deterministic checks on every answer, LLM judge on a sample |
| 2 | 6.2 | `app/observability/traced_port.py` — spans for LLM, embedding and retrieval calls under one `trace_id` |
| 3 | 6.3 | `app/compliance/` — read-only SQL guardrail, PII redaction (e-mail, SSN, CPF) |
| 4 | 6.4 | `LocalLLM` + `INFERENCE_MODE=cloud\|local` |
| 5 | 6.5 | `QueryBudget` (core policy) + `BudgetedLLMPort` (enforcement); 429 when exceeded |
| 6 | 6.6 | `LocalEmbeddings` + `DEPLOYMENT_MODE=cloud\|sovereign` |

## How a `/query` request is wired now

```
HTTP adapter ── trace_id + fresh QueryBudget ──▶ make_query_handler()
                                                     │
AnswerQuestionHandler(llm=Budgeted(Traced(PiiGuardrail(OpenAILLM|LocalLLM))),
                      embedder=Traced(OpenAIEmbeddings|LocalEmbeddings),
                      retriever=Traced(QdrantRetriever))
                                                     │
                     run_deterministic_checks(result) ── sampled ──▶ judge_answer_quality()
```

## Run it fully local (no cloud calls)

```bash
ollama pull qwen2.5:7b && ollama pull nomic-embed-text
docker compose up -d
DEPLOYMENT_MODE=sovereign PRIVATE_QDRANT_URL=http://localhost:6333 uv run uvicorn main:api
```

## Notes for readers of the book

- 6.2 names `TracedEmbeddingPort` and `TracedRetrievalPort` without listing them; both are here, and retrieval also logs provenance (result count and top score).
- 6.5: the default budget is 5 LLM calls per request rather than 3, because the 5.3 answer graph can legitimately use classify + answer + reformulate + answer.
- 6.3's SQL guardrail also blocks stacked statements (`SELECT 1; DROP …`), and the PII guardrail adds Brazil's CPF next to the US SSN.
