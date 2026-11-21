# Every chapter runs the same four gates. `make check` is what CI runs.
.PHONY: install test typecheck boundaries lint check

install:      ## create .venv and install everything (needs uv: https://docs.astral.sh/uv/)
	uv sync

test:         ## the test harness
	uv run pytest

typecheck:    ## the type checker, as a build gate
	uv run mypy .

boundaries:   ## the boundary enforcer (import-linter)
	uv run lint-imports

lint:
	uv run ruff check .

check: lint typecheck boundaries test
