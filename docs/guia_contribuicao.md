# Guia de Contribuicao

## Branches

- `feature/<numero-issue>-descricao-curta`
- `fix/<numero-issue>-descricao-curta`
- `refactor/<numero-issue>-descricao-curta`
- `docs/<numero-issue>-descricao-curta`
- `chore/<numero-issue>-descricao-curta`

## Commits

Use Conventional Commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`, `ci:`.

Autores do projeto:

- Gabriel Di Vanna Camargo `<gabriel_camargo@usp.br>` - tech lead
- Nicolas Caldas Borsari `<nickborsari@gmail.com>` - produto e validacao
- Caio Nicoluzzi Vieira `<caionv@usp.br>` - backend/dominio
- Felipe Sousa dos Santos `<felipesousa@usp.br>` - frontend

## Pull requests

Todo PR deve conter issue vinculada, resumo, checklist de testes, impacto em metricas e screenshots quando alterar UI.

## Validacao local

```bash
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv sync --extra dev
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run pytest
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run ruff check .
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run pylint app --fail-under=9.0 --persistent=no
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run radon cc app -s -a
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run radon mi app -s
```
