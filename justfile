default: sync format lint type

# sync environment with project dependencies
sync:
    uv sync
    uv pip install --editable .

# update project dependencies
update:
    uv sync --upgrade
    uv pip install --editable .

# run formatter
format:
    uvx ruff format .

# run linter
lint:
    uvx ruff check .

# run type checker
type:
    uv run pyright .

# run tests

alias tests := test

test target="":
    #!/bin/bash
    set -euo pipefail
    IFS=$'\n\t'

    uv sync --group dev

    target="{{ target }}"
    if [ -z "$target" ]; then
        uv run pytest -s ./tests
    else
        uv run pytest -s "$target"
    fi

# run scraper
run: sync
    uv run src/WikipediaScraper/wikipedia_scraper.py
