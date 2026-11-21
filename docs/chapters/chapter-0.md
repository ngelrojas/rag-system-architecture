# Chapter 0 — Setting up the workshop

**Book:** Part 0, section 0.5 · **Branch:** `feature/chapter-0`

Nothing in this branch is a RAG system yet. It is the bench the rest of the book builds on — the three tools from 0.5 and the folders the code will grow into.

| Tool | What it proves | Command |
|---|---|---|
| Test harness — pytest | Ports are real ports; adapters can be swapped for fakes | `make test` |
| Type checker — mypy | Adapters actually match their ports' shapes | `make typecheck` |
| Boundary enforcer — import-linter | The domain never imports an adapter | `make boundaries` |

## Files

```
.importlinter          the boundary contract from 0.5
.python-version        Python 3.12 — pinned so every reader starts from the same state
pyproject.toml         dependencies and tool configuration (uv)
Makefile               make check = lint + typecheck + boundaries + tests
.github/workflows/     the same gates, in CI
domain/  adapters/     empty on purpose: the folders are a promise
tests/test_workshop.py proves the bench works
```

> **Note for readers of the book:** 0.5 sketches the contract with a package called `docintel`. The repository uses top-level `domain` and `adapters` packages, which is what Parts I and II use; Part III moves everything into `app/`.

## Try it

```bash
make install
make check
```

Then break the boundary on purpose: add `import adapters` to `domain/__init__.py` and run `make boundaries`. The contract fails. Remove the line.
