# Inventario do repositorio original

Origem lida em modo somente leitura: `~/Projects/webdev/bolao-dos-noia/`.

## Resumo quantitativo

- Python de aplicacao: 5.162 linhas em `app/`.
- Rotas mais volumosas: `live.py` 734, `bracket.py` router 610, `bets.py` 509, `admin.py` 505, `compare.py` 475.
- Dominio misturado com persistencia: `scoring.py` 437, `bracket.py` 411, `chart.py` 374, `sportsdata.py` 415.
- Frontend acumulado: `public/css/style.css` 6.106 linhas, `leaderboard_chart.html` 771 linhas, muitos partials especificos.
- Testes existentes: smoke de rotas e regressao de snapshots.

## Features reais identificadas

- Login por nickname/senha e primeiro acesso por codigo de convite.
- Complemento de perfil com senha.
- Gating por estado de usuario: sem login, sem perfil, sem palpite, ativo e admin.
- Cadastro e manutencao minima de usuarios por admin.
- Edicao de palpites de grupos, desempates, melhores terceiros e mata-mata.
- Resumo e visualizacao completa do proprio palpite.
- Visualizacao de palpites de terceiros quando permitido.
- Comparativo geral, 1x1 e matriz de classificados no mata-mata.
- Pagina ao vivo com placares, jogos e pontuacao provisional.
- Consolidado oficial da Copa com classificacao de grupos e chave.
- Ranking geral com regras do bolao e grafico historico.
- Snapshots incrementais do leaderboard por partida finalizada.
- Sync de fixtures/resultados via ESPN, com fallback planejado para football-data.
- Seed inicial de times e jogos da Copa 2026.

## Decisoes por categoria

### Backend

| Arquivo original | Decisao | Motivo |
| --- | --- | --- |
| `app/models.py` | mover/refatorar | Modelo cobre entidades essenciais e sera preservado com nomes e comentarios limpos. |
| `app/config.py` | mover/refatorar | Settings simples, precisa `.env.example` seguro e senha admin nao hardcoded. |
| `app/db.py` | reescrever parcial | Mantem SQLite/libsql, remove migracoes oportunistas e logs soltos do import. |
| `app/auth.py` | manter | Bcrypt simples e valido. |
| `app/security.py` | manter/refatorar | CSRF/rate limit continuam, com API menor. |
| `app/deps.py` | refatorar | Gating e helpers uteis, mas consultas raw ficam isoladas. |
| `app/main.py` | reescrever | Middleware e montagem do app ficam mais claros e sem init ruidoso no import. |
| `app/scoring.py` | refatorar/fundir | Regra de pontuacao vira `domain/pontuacao.py`; consultas ficam em `services/ranking.py`. |
| `app/bracket.py` | refatorar/fundir | Resolver de bracket vira dominio; sync de palpites vira servico. |
| `app/standings.py` | mover/refatorar | Classificacao por palpite e desempate sao dominio puro. |
| `app/chart.py` | refatorar | Payload do grafico vira servico pequeno; template SVG gigante descartado. |
| `app/sportsdata.py` | refatorar | Cliente ESPN e aplicacao de updates ficam em `services/sincronizacao.py`. |
| `app/recompute_snapshots.py` | mover/refatorar | Vira comando CLI. |
| `app/sync_fixtures.py` | mover/refatorar | Vira comando CLI. |
| `app/seed.py` | mover/refatorar | Seed oficial permanece, com CLI explicita. |
| `app/gen_codes.py`, `seed_fake.py`, `seed_delta_demo.py` | descartar | Scripts temporarios/demo; nao entram no minimo operacional. |
| `app/flags.py`, `templates_env.py` | fundir/refatorar | Helpers de flag e Jinja ficam enxutos. |

### Rotas

| Arquivo original | Decisao | Motivo |
| --- | --- | --- |
| `routers/auth.py` | refatorar | Fluxo essencial permanece; divergencia antiga de testes sera corrigida. |
| `routers/pages.py` | refatorar | Home, secoes, consulta e regulamento continuam com menos dependencias externas. |
| `routers/bets.py` | reescrever parcial | Edicao permanece, mas menos HTMX e menos partials duplicados. |
| `routers/bracket.py` | fundir | Resumo/completo do palpite entra em rotas menores de viewer/palpites. |
| `routers/compare.py` | refatorar | Mantem geral, 1x1 e mata-mata com tabelas mais simples. |
| `routers/leaderboard.py` | refatorar | Usa servico unico de ranking e grafico simplificado. |
| `routers/live.py` | reescrever parcial | Mantem ao vivo/consolidado sem duplicar logica de bracket oficial. |
| `routers/admin.py` | refatorar | Mantem seed/sync/admin users; remove endpoints experimentais. |
| `routers/perfil.py`, `viewer.py` | fundir/refatorar | Perfil e visualizacao de terceiros ficam menores. |

### Templates e static

| Arquivo original | Decisao | Motivo |
| --- | --- | --- |
| `templates/base.html` | reescrever | Navegacao e mensagens padronizadas. |
| `templates/index.html` | reescrever | Home operacional para usuario logado. |
| `templates/auth/*` | refatorar | Formulario unico de login e primeiro acesso. |
| `templates/bets/aposta.html` | reescrever parcial | Mantem edicao de grupos e mata-mata com markup direto. |
| `templates/compare/*` | reescrever | Tabelas simples substituem grids grandes. |
| `templates/leaderboard/leaderboard.html` | reescrever | Ranking, regras e grafico no mesmo fluxo. |
| `templates/live/live.html` | refatorar | Ao vivo e consolidado usam componentes compactos. |
| `templates/partials/*` | descartar/fundir | Parciais so ficam quando reduzem duplicacao real. |
| `public/css/style.css` | reescrever | CSS unico menor com tokens, tabelas, forms, cards e nav. |
| `public/js/bracket.js`, `countdown.js`, `ticker.js`, `palpite-download.js` | descartar | Nao sao essenciais para o minimo funcional. |
| `public/js/live.js` | reescrever minimo | Polling/auto-refresh simples se necessario. |
| `public/assets/favicon.*`, `trofeu_copa.png` | manter | Ativos reais do produto. |

### Dados, docs e deploy

| Arquivo original | Decisao | Motivo |
| --- | --- | --- |
| `data/seed/worldcup-2026.json` | manter | Base oficial de times e jogos. |
| `data/roster.json` | descartar | Potencialmente sensivel e substituido por admin users. |
| `docs/schema.md`, `architecture.md`, `api-integration.md`, `frontend-style.md` | refatorar | Conteudo util sera consolidado nos docs novos. |
| `SCORING.md`, `REGULAMENTO.md` | fundir | Regras entram em docs e pagina de ranking/regulamento. |
| `.env.example`, `pyproject.toml`, `requirements.txt`, `vercel.json` | refatorar | Configuracao alvo usa `pyproject.toml`, `.env.example` e CI. |

### Testes

| Arquivo original | Decisao | Motivo |
| --- | --- | --- |
| `tests/test_leaderboard_snapshots.py` | manter/refatorar | Regressao critica. |
| `tests/test_smoke.py` | refatorar | Fluxos mudaram; preservar cobertura de rotas essenciais. |
| `tests/conftest.py` | refatorar | Isolamento SQLite continua. |

## Arquivos descartados de forma explicita

- Ambientes virtuais: `.venv`, `.venv312`.
- Caches: `.pytest_cache`, `*.egg-info`.
- Banco local real e artefatos em `data/` que nao sejam seed publico.
- Scripts temporarios ou de demo: `seed_fake.py`, `seed_delta_demo.py`, `gen_codes.py`.
- Documentacao de ferramenta ou historica que nao orienta manutencao atual.
- CSS e JS acumulados sem tela correspondente no alvo.

## Segunda triagem aplicada

Apos comparar novamente rotas e modelos da origem, foram recuperadas features pequenas que tinham valor real e nao exigiam copiar os modulos grandes:

- `routers/perfil.py`: mantido como modulo novo e enxuto para troca de nome, nickname e senha.
- `routers/bets.py`: recuperada a intencao de desempate manual de grupos e melhores terceiros.
- `routers/viewer.py`: adicionadas rotas compativeis `/palpite/{id}/resumo`, `/palpite/{id}/completa` e CSV.
- `routers/live.py`: adicionado detalhe de palpites por jogo de grupo, com visibilidade limitada antes do deadline.

Continuaram fora do alvo:

- Bracket interativo completo com `BetMatch`, por ainda exigir uma modelagem maior para nao recriar o acoplamento antigo.
- HTMX/partials do original, porque a versao sem JS cobre o fluxo essencial.
- Admin avancado de edicao/exclusao em massa, porque o minimo operacional ja cobre cadastro e liberacao pontual.
