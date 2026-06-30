# 0001 - Reconstrucao seletiva

## Status

Aceita.

## Contexto

O repositorio original acumulou rotas grandes, templates redundantes, CSS extenso e scripts de apoio historicos. A meta do alvo e preservar o produto, nao a historia acidental.

## Decisao

Migrar somente os conceitos estaveis: modelos, seed da Copa, regras de pontuacao, bracket, snapshots, login, administracao minima, sync e telas principais. Reescrever a interface com menos templates e CSS unico em `app/static/css/app.css`.

## Consequencias

Algumas telas ficam mais simples visualmente, mas com superficie menor para manutencao. O dominio de pontuacao passa a ser a fonte de verdade para ranking, comparativos e snapshots.

