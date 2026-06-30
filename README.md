# Bolao Profissa

Reconstrucao profissional do Bolao dos Noia para a Copa de 2026. O projeto preserva os fluxos reais do produto e reduz codigo morto, duplicacao de templates, CSS acumulado e scripts temporarios.

## Setup local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
python -m app.cli.seed
uvicorn app.main:app --reload
```

App local: `http://127.0.0.1:8000`.

## Comandos operacionais

```bash
pytest
ruff check .
pylint app
radon cc app -s -a
radon mi app -s
python -m app.cli.sync_fixtures
python -m app.cli.recompute_snapshots --apply
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

