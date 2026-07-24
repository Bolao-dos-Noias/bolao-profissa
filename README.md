# Bolão Profissa

[![CI](https://github.com/Bolao-dos-Noias/bolao-profissa/actions/workflows/ci.yml/badge.svg)](https://github.com/Bolao-dos-Noias/bolao-profissa/actions/workflows/ci.yml)

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

## Backlog e ciclos de trabalho

O projeto trabalha em ciclos organizados como Milestones do GitHub, cada um com um tema, issues com responsável e critérios de aceite definidos antes do início do trabalho. O histórico completo de ciclos, milestones e issues (passadas e planejadas) está em [docs/issues_milestones.md](docs/issues_milestones.md). O ciclo atual é o **Ciclo 3**, focado em fechar lacunas identificadas em [faltantes.md](faltantes.md) frente ao repositório de referência (bracket/mata-mata, polimento de live/compare/ranking, perfil/admin, testes e documentação).

## Como contribuir

1. Escolha ou abra uma issue vinculada a um milestone do ciclo atual.
2. Crie uma branch a partir de `main` seguindo o padrão `tipo/<issue>-descricao-curta`, por exemplo `feature/29-bracket-mata-mata` ou `docs/26-readme-onboarding`. Tipos aceitos: `feature`, `fix`, `refactor`, `docs`, `chore`.
3. Faça commits no padrão [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`, `ci:`).
4. Rode a [validação local](#como-validar-o-projeto) antes de abrir o PR.
5. Abra o PR usando o template do repositório: ele deve vincular a issue, descrever o que mudou, listar os testes/validações realizados e indicar o impacto esperado (inclua screenshots se alterar UI).
6. Todo PR passa pelo CI (ruff, pytest, pylint, radon) e precisa de revisão do tech lead antes do merge.

Guia completo de contribuição, papéis e convenções: [docs/guia_contribuicao.md](docs/guia_contribuicao.md).

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
