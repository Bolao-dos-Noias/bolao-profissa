# Arquitetura

## Camadas

- `app/routers`: entrada HTTP, validacao leve e renderizacao de templates.
- `app/services`: casos de uso, consultas coordenadas e transacoes.
- `app/domain`: regras puras de classificacao, bracket, pontuacao e snapshots.
- `app/repositories`: consultas persistentes compartilhadas quando reduzem duplicacao.
- `app/cli`: comandos operacionais para seed, sync e recompute.
- `app/templates`: Jinja com logica minima.
- `app/static`: CSS e JavaScript reduzidos ao necessario.

## Fonte de verdade da pontuacao

`app/domain/pontuacao.py` define pesos, ordenacao, desempates e serializacao de snapshots. `app/services/ranking.py` converte dados persistidos para essa regra. Ranking, comparativos, live e recompute consomem o mesmo servico.

## Banco

O alvo preserva SQLModel, SQLite local e Turso/libsql. Dados sensiveis ficam fora do Git e sao configurados por `.env`.

