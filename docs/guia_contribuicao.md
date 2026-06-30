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
pytest
ruff check .
pylint app
radon cc app -s -a
radon mi app -s
```

