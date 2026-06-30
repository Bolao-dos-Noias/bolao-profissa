#!/usr/bin/env bash
set -euo pipefail

export UV_CACHE_DIR="${UV_CACHE_DIR:-.uv-cache}"
export UV_PROJECT_ENVIRONMENT="${UV_PROJECT_ENVIRONMENT:-.venv312}"

uv run ruff check .
uv run pylint app --fail-under=9.0 --persistent=no
uv run radon cc app -s -a
uv run radon mi app -s
