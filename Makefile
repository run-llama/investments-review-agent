.PHONY: lint lint-check format format-check typecheck lint-ui install-ui-deps

all: lint format typecheck lint-ui

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
	uv run ty check src/investments_review/

lint-ui: install-ui-deps
	$(info ****************** linting UI ******************)
	cd ui/ && pnpm run lint && cd ..

install-ui-deps:
	$(info ****************** installing UI deps ******************)
	cd ui/ && pnpm install --no-frozen-lockfile && cd ..
