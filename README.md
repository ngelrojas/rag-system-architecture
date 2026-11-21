# RAG Systems Architecture — companion code

Companion repository for the book **RAG Systems Architecture — For AI Engineers: Building Production RAG with Real Software Architecture**.

The book builds **one system** — a document intelligence service — and refactors it chapter by chapter. This repository follows the same path: **every chapter has its own branch**, and each branch contains exactly the code that chapter leaves behind. `master` holds the complete reference system from Part VII.

## Chapters and branches

| Chapter | Book part | Branch | What the code adds |
|---|---|---|---|
| 0 | Part 0 — Why Your RAG Prototype Won't Survive Production | `feature/chapter-0` | The workshop: Python 3.12, test harness, type checker, boundary enforcer, CI |
| 1 | Part I — The Model Layer | `feature/chapter-1` | `LLMPort`, the OpenAI adapter, `FakeLLM`, the first contract |
| 2 | Part II — The Retrieval Path | `feature/chapter-2` | The naive pipeline, chunking, `EmbeddingPort`, `VectorStorePort`, orchestrators |
| 3 | Part III — Software Architecture | `feature/chapter-3` | `app/` hexagonal layout, composition root, rollback policy, enforced boundaries, outbox |
| 4 | Part IV — CQRS | `feature/chapter-4` | Commands and queries, `RetrievalPort`, separate handlers |
| 5 | Part V — Orchestration & Agentic RAG | `feature/chapter-5` | LangGraph as a driving adapter, human-in-the-loop, multi-agent routing, NLQ |
| 6 | Part VI — Cross-Cutting Concerns | `feature/chapter-6` | Evaluation, observability, guardrails, local inference, budgets, sovereignty |
| 7 | Part VII — The Complete Reference System | `feature/chapter-7` → `master` | Diagrams as code, end-to-end test, offline demo |

Each branch starts from the previous one, so `git log` on a branch reads like the book: **one commit per section**.

```bash
git checkout feature/chapter-3          # the code exactly as Part III leaves it
git log --oneline feature/chapter-3..feature/chapter-4   # what Part IV changes, section by section
git diff feature/chapter-3 feature/chapter-4  # the whole Part IV refactor in one view
```

## Setup

Requirements: [uv](https://docs.astral.sh/uv/) (it installs Python 3.12 for you), and Docker for the chapters that use Qdrant and Postgres.

```bash
make install     # uv sync — creates .venv with the pinned Python
make check       # lint, type check, architectural boundaries, tests
cp .env.example .env   # only needed when you call real services
```

`make check` runs the same four gates as CI (`.github/workflows/lint.yml`). Every branch passes them without API keys: the tests use the fakes the book builds.

Each chapter's notes are in [`docs/chapters/`](docs/chapters/).

## License

Code: MIT (see [LICENSE](LICENSE)). The book text is not part of this repository.
