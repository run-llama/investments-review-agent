.PHONY: lint lint-check format format-check typecheck

all: test lint format typecheck

lint:
	$(info ****************** linting ******************)
	uv run ruff check --fix

lint-check:
	$(info ****************** checking linting ******************)
	uv run ruff check

format:
	$(info ****************** formatting ******************)
	uv run ruff format

format-check:
	$(info ****************** checking formatting ******************)
	uv run ruff format --check

typecheck:
	$(info ****************** type checking ******************)
	uv run ty src/investments_review/

lint-ui:
	$(info ****************** linting UI ******************)
	cd ui/ && npm run lint
