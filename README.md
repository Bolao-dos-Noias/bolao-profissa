# Bolao Profissa

Reconstrucao profissional do Bolao dos Noia para a Copa de 2026. O projeto preserva os fluxos reais do produto e reduz codigo morto, duplicacao de templates, CSS acumulado e scripts temporarios.

## Setup local

```bash
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv sync --extra dev
cp .env.example .env
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run python -m app.cli.seed
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run uvicorn app.main:app --reload
```

App local: `http://127.0.0.1:8000`.

## Comandos operacionais

```bash
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run pytest
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run ruff check .
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run pylint app --fail-under=9.0 --persistent=no
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run radon cc app -s -a
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run radon mi app -s
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run python -m app.cli.sync_fixtures
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run python -m app.cli.recompute_snapshots --apply
```

## Fluxo de equipe

- Branch principal: `main`.
- Branches: `feature/<issue>-descricao`, `fix/<issue>-descricao`, `refactor/<issue>-descricao`, `docs/<issue>-descricao`, `chore/<issue>-descricao`.
- Commits: Conventional Commits.
- PRs: vinculam issue, listam testes, impacto de metricas e screenshots quando houver UI.

Documentacao principal:

- [Arquitetura](docs/arquitetura.md)
- [Guia de contribuicao](docs/guia_contribuicao.md)
- [Metricas](docs/metricas.md)
- [Inventario da origem](docs/inventario_origem.md)
- [Relatorio final](docs/relatorio_final.md)
