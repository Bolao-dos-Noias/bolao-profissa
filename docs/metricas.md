# Metricas

## Baseline inicial

Coletado na primeira reconstrucao limpa com `uv` e Python 3.12.

```bash
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv sync --extra dev
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run pytest --cov=app --cov-report=term-missing
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run ruff check .
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run pylint app --fail-under=9.0 --persistent=no
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run radon cc app -s -a
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run radon mi app -s
```

Resultados:

- `uv run pytest`: 13 passed em 8.17s.
- `uv run pytest --cov=app --cov-report=term-missing`: 13 passed em 10.43s; cobertura total 62%.
- `uv run ruff check .`: passou.
- `uv run pylint app --fail-under=9.0 --persistent=no`: 9.19/10.
- `uv run radon cc app -s -a`: complexidade media A, 4.14.
- `uv run radon mi app -s`: todos os modulos em A.

Pontos de atencao do baseline:

- `app/domain/classificacao.py::compute_standings`: D, 21.
- `app/services/seed.py::seed`: C, 20.
- `app/main.py::WorkflowGateMiddleware.__call__`: C, 20.
- `app/routers/leaderboard.py::_chart_payload`: C, 17.
- `app/services/sincronizacao.py::_live_clock_from_espn`: C, 16.

Interpretacao:

- A cobertura inicial cobre os fluxos de autenticacao, gating, ranking e snapshots incrementais, mas ainda precisa crescer em frontend, admin, sync ESPN real e seed.
- O score do pylint fica acima do gate de 9.0, apesar de avisos esperados de SQLModel e complexidade residual em rotas/servicos que devem ser alvo das proximas milestones.
- A complexidade media esta saudavel, mas as funcoes listadas acima devem ser refatoradas conforme as tarefas de Caio e Gabriel.

## Interpretacao

- Complexidade ciclomatica alta em `routers` indica regra de negocio vazando da camada de servico.
- Maintainability index baixo em templates/CSS sugere duplicacao ou UI dificil de revisar.
- Score do pylint deve ser acompanhado por milestone, sem transformar avisos em meta vazia.
