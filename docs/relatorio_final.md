# Relatorio final da reconstrucao inicial

## Mantido

- Modelos centrais: usuarios, times, partidas, palpites de grupo, palpites de mata-mata, desempates, settings e snapshots.
- Seed publico `data/seed/worldcup-2026.json`.
- Compatibilidade com SQLite local e Turso/libsql.
- Login por nickname/senha e primeiro acesso por codigo de convite.
- Fluxo de complemento de perfil.
- Edicao posterior de nome, nickname e senha com confirmacao da senha atual.
- Edicao de palpites enquanto permitido.
- Desempates manuais de grupos e selecao dos melhores terceiros.
- Ranking geral, regras do bolao e historico por snapshots.
- Sync ESPN em servico isolado.
- Recompute de snapshots historicos.
- Comparativos geral, 1x1 e mata-mata em versao enxuta.
- Ao vivo, palpites por jogo de grupo, consolidado oficial e consulta de jogos.
- Exportacao CSV do palpite completo.
- Admin minimo para seed/sync/cadastro/liberacao pontual de edicao.

## Removido

- Ambientes virtuais, caches, bancos locais reais, logs e egg-info.
- `data/roster.json`, por poder conter dados operacionais e por ter sido substituido pelo cadastro via admin.
- Scripts temporarios/demo como seed fake, delta demo, geracao avulsa de codigos e seed Claude.
- CSS acumulado de 6.106 linhas e JS sem fluxo essencial.
- Templates parciais duplicados e componentes HTMX especificos que aumentavam acoplamento.
- Router de bracket original com mais de 600 linhas; a intencao foi preservada por servicos e views menores.
- Documentacao de ferramenta/historica que nao orientava manutencao do produto.

## Reescrito

- `app/main.py`: app FastAPI com middleware ASGI puro para evitar threadpool em testes e manter gating explicito.
- `app/domain/pontuacao.py`: desempate, serializacao e parsing de snapshots como dominio puro.
- `app/domain/classificacao.py`: classificacao prevista por palpites.
- `app/services/ranking.py`: unica entrada para ranking, live ranking e snapshots.
- `app/services/sincronizacao.py`: sync ESPN e criacao incremental de snapshots.
- `app/services/seed.py`: seed idempotente baseado no JSON publico.
- `app/services/palpites.py`: contexto unico para grupos, desempates, terceiros e mata-mata.
- `app/routers/perfil.py`: edicao de dados de perfil em modulo pequeno.
- `app/routers/viewer.py`: resumo/completo e CSV sem depender do bracket antigo.
- Templates e CSS: UI funcional, densa e previsivel com `app/static/css/app.css`.
- Testes: smoke de fluxos e regressao de snapshots incrementais.

## Metricas iniciais

- Testes: 17 passed.
- Cobertura: 66%.
- Ruff: passou.
- Pylint: 9.26/10 com gate `fail-under=9.0`.
- Radon CC: media A, 4.05.
- Radon MI: todos os modulos A.

## Plano por pessoa

### Gabriel

- Manter `WorkflowGateMiddleware` em C ou melhor e reduzir retornos restantes.
- Configurar branch protection e PR template no provedor Git.
- Revisar CI e manter o gate de qualidade por milestone.
- Liderar refatoracao de `services/ranking.py` e payload do grafico.

### Caio

- Ampliar testes de pontuacao de grupos, zebras, mata-mata e campeao.
- Refatorar `domain/classificacao.py::compute_standings`.
- Testar sync ESPN com fixtures gravadas e cenarios de mata-mata.
- Cobrir seed e recompute com regressao de dados reais.

### Felipe

- Validar responsividade de ranking, aposta, comparativos e admin.
- Reduzir atrito da tela de aposta, principalmente selecao de terceiros e mata-mata.
- Criar screenshots de PR para alteracoes de UI.
- Avaliar se algum JS minimo agrega valor sem recriar acumulacao.

### Nicolas

- Validar regras do bolao com dados reais e exemplos manuais.
- Conferir textos de regulamento, nomes de fases e aceite funcional.
- Validar seed da Copa e nomes das selecoes.
- Validar exportacao CSV e visualizacao de palpites de terceiros antes do deadline real.

## Proximos PRs sugeridos

- `refactor/7-dominio-pontuacao`: quebrar ranking/snapshots em unidades menores.
- `test/8-pontuacao-zebras-mata-mata`: ampliar cobertura de regras.
- `refactor/14-css-base`: polimento visual e responsivo.
- `docs/19-metricas-finais`: atualizar metricas apos cada milestone.
