# Bolão Profissa

Bolão Profissa é uma aplicação web para organizar e acompanhar um bolão da Copa do Mundo de 2026 com foco em usabilidade, regras de pontuação claras, ranking público e uma arquitetura mais profissional do que a versão anterior.

O projeto foi reconstruído com uma abordagem mais limpa e sustentável, separando responsabilidades entre rotas, serviços, domínio, modelos e templates. A ideia é preservar o comportamento do produto original, mas com melhores práticas de engenharia de software, testes e documentação.

## Visão geral

A plataforma oferece:

- autenticação e onboarding de usuários;
- cadastro de palpites para fases de grupos, desempates e terceiros;
- cálculo de pontuação com regras de grupo, zebras e mata-mata;
- ranking público com histórico de snapshots;
- páginas de consulta, comparação, live e perfil;
- fluxo administrativo para seed, sincronização e recompute de dados.

## Stack principal

- Python 3.12+
- FastAPI
- SQLModel / SQLAlchemy
- Jinja2
- Uvicorn
- Pytest, Ruff, Pylint e Radon

## Estrutura do repositório

- app/: aplicação principal, incluindo routers, serviços, domínio, modelos e CLI.
- data/: dados e fixtures usados para seed.
- docs/: arquitetura, contribuição, métricas e documentação histórica.
- tests/: testes de smoke e fluxos críticos.
- scripts/: utilitários operacionais.

## Pré-requisitos

- Python 3.12
- uv

## Como rodar localmente

```bash
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv sync --extra dev
cp .env.example .env
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run python -m app.cli.seed
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run uvicorn app.main:app --reload
```

A aplicação fica disponível em http://127.0.0.1:8000.

## Como validar o projeto

```bash
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run pytest
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run ruff check .
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run pylint app --fail-under=9.0 --persistent=no
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run radon cc app -s -a
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run radon mi app -s
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run python -m app.cli.sync_fixtures
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run python -m app.cli.recompute_snapshots --apply
```

## Padrões de projeto

O projeto segue boas práticas de engenharia de software, com foco em:

- arquitetura em camadas e separação de responsabilidades;
- domínio e regras de negócio centralizadas;
- testes automatizados para fluxos críticos;
- documentação operacional e de contribuição;
- fluxo de trabalho com branches, commits semânticos e pull requests.

## Fluxo de contribuição

- Branch principal: main
- Branches de trabalho: feature/<issue>-descricao, fix/<issue>-descricao, refactor/<issue>-descricao, docs/<issue>-descricao, chore/<issue>-descricao
- Commits: Conventional Commits
- PRs: devem vincular issue, listar testes realizados e indicar impacto esperado

## Autores do projeto

- Nicolas Caldas Borsari — produto e validação
- Caio Nicoluzzi Vieira — backend e domínio
- Felipe Sousa dos Santos — frontend e experiência
- Gabriel Di Vanna Camargo — tech lead e revisão final

## Documentação principal

- [Arquitetura](docs/arquitetura.md)
- [Guia de contribuição](docs/guia_contribuicao.md)
- [Métricas](docs/metricas.md)
- [Inventário da origem](docs/inventario_origem.md)
- [Relatório final](docs/relatorio_final.md)
