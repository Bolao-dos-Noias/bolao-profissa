# Relatório final da reconstrução inicial

## Mantido

- Modelos centrais: usuários, times, partidas, palpites de grupo, palpites de mata-mata, desempates, settings e snapshots.
- Seed público `data/seed/worldcup-2026.json`.
- Compatibilidade com SQLite local e Turso/libsql.
- Login por nickname/senha e primeiro acesso por código de convite.
- Fluxo de complemento de perfil.
- Edição posterior de nome, nickname e senha com confirmação da senha atual.
- Edição de palpites enquanto permitido.
- Desempates manuais de grupos e seleção dos melhores terceiros.
- Ranking geral, regras do bolão e histórico por snapshots.
- Sync ESPN em servico isolado.
- Recompute de snapshots históricos.
- Comparativos geral, 1x1 e mata-mata em versão enxuta.
- Ao vivo, palpites por jogo de grupo, consolidado oficial e consulta de jogos.
- Exportação CSV do palpite completo.
- Admin mínimo para seed/sync/cadastro/liberacao pontual de edição.

## Removido

- Ambientes virtuais, caches, bancos locais reais, logs e egg-info.
- `data/roster.json`, por poder conter dados operacionais e por ter sido substituido pelo cadastro via admin.
- Scripts temporários/demo como seed fake, delta demo e geração avulsa de códigos.
- CSS acumulado de 6.106 linhas e JS sem fluxo essencial.
- Templates parciais duplicados e componentes HTMX específicos que aumentavam acoplamento.
- Router de bracket original com mais de 600 linhas; a intenção foi preservada por serviços e views menores.
- Documentação de ferramenta/histórica que não orientava manutenção do produto.

## Reescrito

- `app/main.py`: app FastAPI com middleware ASGI puro para evitar threadpool em testes e manter gating explicito.
- `app/domain/pontuacao.py`: desempate, serialização e parsing de snapshots como domínio puro.
- `app/domain/classificacao.py`: classificação prevista por palpites.
- `app/services/ranking.py`: única entrada para ranking, live ranking e snapshots.
- `app/services/sincronizacao.py`: sync ESPN e criação incremental de snapshots.
- `app/services/seed.py`: seed idempotente baseado no JSON público.
- `app/services/palpites.py`: contexto único para grupos, desempates, terceiros e mata-mata.
- `app/routers/perfil.py`: edição de dados de perfil em módulo pequeno.
- `app/routers/viewer.py`: resumo/completo e CSV sem depender do bracket antigo.
- Templates e CSS: UI funcional, densa e previsível com `app/static/css/app.css`.
- Testes: smoke de fluxos e regressão de snapshots incrementais.

## Métricas iniciais

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
- Liderar refatoração de `services/ranking.py` e payload do gráfico.

### Caio

- Ampliar testes de pontuação de grupos, zebras, mata-mata e campeão.
- Refatorar `domain/classificacao.py::compute_standings`.
- Testar sync ESPN com fixtures gravadas e cenários de mata-mata.
- Cobrir seed e recompute com regressao de dados reais.

### Felipe

- Validar responsividade de ranking, aposta, comparativos e admin.
- Reduzir atrito da tela de aposta, principalmente seleção de terceiros e mata-mata.
- Criar screenshots de PR para alteracções de UI.
- Avaliar se algum JS mínimo agrega valor sem recriar acumulação.

### Nicolas

- Validar regras do bolão com dados reais e exemplos manuais.
- Conferir textos de regulamento, nomes de fases e aceite funcional.
- Validar seed da Copa e nomes das seleções.
- Validar exportação CSV e visualização de palpites de terceiros antes do deadline real.

## Próximos PRs sugeridos

- `refactor/7-dominio-pontuacao`: quebrar ranking/snapshots em unidades menores.
- `test/8-pontuacao-zebras-mata-mata`: ampliar cobertura de regras.
- `refactor/14-css-base`: polimento visual e responsivo.
- `docs/19-metricas-finais`: atualizar métricas após cada milestone.
