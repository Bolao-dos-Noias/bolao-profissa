# Faltantes do `bolao-profissa` em relação ao `bolao-dos-noia`

Este arquivo registra, de forma prática, o que ainda falta no `bolao-profissa` quando comparado ao repositório de referência `bolao-dos-noia`.

Critério usado:
- comparei a árvore de arquivos dos dois projetos;
- removi ruído de ambiente e VCS como `.git`, `.venv`, `__pycache__` e artefatos compilados;
- classifiquei o resultado em três grupos:
  1. features presentes no original e ausentes no alvo;
  2. features presentes nos dois, mas ainda divergentes;
  3. arquivos de suporte, operação e documentação.

## 1. Features que existem no original e ainda não estão no `bolao-profissa`

### Bracket e mata-mata

O original tem um bloco próprio de bracket que não está equivalente no alvo:

- `app/routers/bracket.py`
- `app/templates/bracket/bracket.html`
- `app/templates/bracket/linear.html`
- `app/templates/partials/bracket_section.html`
- `app/templates/partials/bracket_match.html`
- `app/templates/partials/stage_r32.html`
- `app/templates/partials/stage_ko.html`
- `app/templates/partials/thirds_order.html`
- `app/templates/partials/thirds_and_bracket.html`
- `app/templates/partials/match_picks.html`
- `app/templates/partials/ko_pick_response.html`

### Comparação

O conjunto de comparação do original ainda é maior:

- `app/templates/compare/_grid.html`
- `app/templates/compare/_mata_grid.html`

### Live

O original tem mais telas e partials de live:

- `app/templates/live/consolidado.html`
- `app/templates/live/resultados.html`
- `app/templates/live/palpites_jogo.html`
- `app/templates/partials/live_panel.html`

### Grupo e respostas dinâmicas

O fluxo de grupo no original tem mais componentes parciais:

- `app/templates/partials/grupo_card.html`
- `app/templates/partials/group_card_response.html`
- `app/templates/partials/group_match.html`
- `app/templates/partials/group_pick_response.html`
- `app/templates/partials/group_standings.html`
- `app/templates/partials/no_match.html`

### Ranking

O ranking do original tem apoio visual e estrutural adicional:

- `app/templates/partials/leaderboard_rows.html`
- `app/templates/partials/leaderboard_chart.html`

### Admin

Há uma tela administrativa adicional no original:

- `app/templates/admin/user_edit.html`

## 2. Features presentes nos dois, mas ainda divergentes

Aqui entram coisas que existem no `bolao-profissa`, mas ainda não estão no mesmo nível do original.

### Frontend principal

O alvo já tem a base das telas principais, mas ainda diverge no detalhamento visual e de interação:

- `app/templates/base.html`
- `app/templates/index.html`
- `app/templates/palpites.html`
- `app/templates/copa.html`
- `app/templates/copa_consulta.html`
- `app/templates/leaderboard/leaderboard.html`
- `app/templates/live/live.html`
- `app/templates/bets/aposta.html`
- `app/templates/perfil/*`

Diferenças prováveis que ainda precisam ser fechadas:
- composição exata do topo;
- menus e navegação com o mesmo comportamento do original;
- microinterações de live, comparação e palpites;
- acabamento visual do CSS e dos assets.

### Autenticação e perfil

O núcleo existe no alvo, mas ainda precisa ser validado contra o original:

- `app/templates/auth/login.html`
- `app/templates/auth/login_codigo.html`
- `app/templates/auth/complete_profile.html`
- `app/templates/perfil/nome.html`
- `app/templates/perfil/nickname.html`
- `app/templates/perfil/senha.html`

### Pontuação e regra

O alvo já tem domínio e serviço de pontuação, mas o original tem mais superfície de regra e apoio:

- `app/domain/pontuacao.py`
- `app/domain/classificacao.py`
- `app/services/palpites.py`
- `app/services/ranking.py`

Isso sugere divergência ainda possível em:
- cálculo de score;
- desempates;
- agregação de classificação;
- consistência com snapshots do original.

## 3. Arquivos de suporte, operação e documentação que ainda faltam

### Operação e empacotamento

- `vercel.json`
- `requirements.txt`
- `CLAUDE.md`
- `SCORING.md`
- `REGULAMENTO.md`
- `api/index.py`
- `bolao_dos_noia.egg-info/*`

### Dados e seed

- `data/.gitkeep`
- `data/bolao-prod-copy.db`
- `data/bolao-prod-copy.before-ko-sync.db`
- `data/roster.json`
- `app/seed_delta_demo.py`
- `app/seed_fake.py`
- `app/claude_seed.py`
- `app/gen_codes.py`
- `app/recompute_snapshots.py`

### Scripts auxiliares

- `scripts/apply_prod_copy_to_turso.sh`
- `scripts/seed_claude_picks.py`

### Testes e cobertura

- `tests/test_leaderboard_snapshots.py`
- `tests/__init__.py`

### Documentação de referência

- `docs/schema.md`
- `docs/frontend-style.md`
- `docs/architecture.md`
- `docs/api-integration.md`

### Frontend público do original

- `public/js/bracket.js`
- `public/js/countdown.js`
- `public/js/live.js`
- `public/js/palpite-download.js`
- `public/js/ticker.js`
- `public/js/frases.txt`
- `public/js/frases2.txt`
- `public/css/style.css`
- `public/assets/*`
- `assets/favicon.png`
- `assets/trofeu_copa.png`

## 4. Leitura prática

O que está mais faltando hoje no `bolao-profissa` é:

1. o pacote completo de `bracket`;
2. os complementos de live, comparação e ranking;
3. o frontend fino com JS e partials do original;
4. os scripts e dados auxiliares de operação;
5. a documentação e empacotamento equivalentes ao repositório de referência.

## 5. Limite desta comparação

Este inventário foi feito por diferença de arquivo, então ele responde bem a:

- “o que existe no original e não existe no alvo?”

Mas ainda não fecha totalmente:

- “o que existe nos dois, mas está funcionalmente diferente?”

Para isso, o próximo passo é abrir os fluxos mais sensíveis e comparar comportamento, não só presença de arquivo.
