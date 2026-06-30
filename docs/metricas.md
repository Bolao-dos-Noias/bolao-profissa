# Metricas

## Baseline inicial

Preencher apos a primeira execucao de:

```bash
pytest --cov=app --cov-report=term-missing
pylint app
radon cc app -s -a
radon mi app -s
```

## Interpretacao

- Complexidade ciclomática alta em `routers` indica regra de negocio vazando da camada de servico.
- Maintainability index baixo em templates/CSS sugere duplicacao ou UI dificil de revisar.
- Score do pylint deve ser acompanhado por milestone, sem transformar avisos em meta vazia.

