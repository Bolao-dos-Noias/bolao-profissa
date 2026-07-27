# Inventário do repositório original

Origem lida em modo somente leitura: `~/Projects/webdev/bolao-dos-noia/`.

## Resumo quantitativo

- Python de aplicação: 5.162 linhas em `app/`.
- Rotas mais volumosas: `live.py` 734, `bracket.py` router 610, `bets.py` 509, `admin.py` 505, `compare.py` 475.
- Dominio misturado com persistência: `scoring.py` 437, `bracket.py` 411, `chart.py` 374, `sportsdata.py` 415.
- Frontend acumulado: `public/css/style.css` 6.106 linhas, `leaderboard_chart.html` 771 linhas, muitos partials especificos.
- Testes existentes: smoke de rotas e regressão de snapshots.

## Features reais identificadas

- Login por nickname/senha e primeiro acesso por codigo de convite.
- Complemento de perfil com senha.
- Gating por estado de usuário: sem login, sem perfil, sem palpite, ativo e admin.
- Cadastro e manutenção mínima de usuários por admin.
- Edicao de palpites de grupos, desempates, melhores terceiros e mata-mata.
- Resumo e visualização completa do próprio palpite.
- Visualização de palpites de terceiros quando permitido.
- Comparativo geral, 1x1 e matriz de classificados no mata-mata.
- Página ao vivo com placares, jogos e pontuação provisional.
- Consolidado oficial da Copa com classificação de grupos e chave.
- Ranking geral com regras do bolão e gráfico histórico.
- Snapshots incrementais do leaderboard por partida finalizada.
- Sync de fixtures/resultados via ESPN, com fallback planejado para football-data.
- Seed inicial de times e jogos da Copa 2026.

## Decisões por categoria

### Backend

| Arquivo original | Decisão | Motivo |
| --- | --- | --- |
| `app/models.py` | mover/refatorar | Modelo cobre entidades essenciais e será preservado com nomes e comentários limpos. |
| `app/config.py` | mover/refatorar | Settings simples, precisa `.env.example` seguro e senha admin não hardcoded. |
| `app/db.py` | reescrever parcial | Mantem SQLite/libsql, remove migrações oportunistas e logs soltos do import. |
| `app/auth.py` | manter | Bcrypt simples e válido. |
| `app/security.py` | manter/refatorar | CSRF/rate limit continuam, com API menor. |
| `app/deps.py` | refatorar | Gating e helpers úteis, mas consultas raw ficam isoladas. |
| `app/main.py` | reescrever | Middleware e montagem do app ficam mais claros e sem init ruidoso no import. |
| `app/scoring.py` | refatorar/fundir | Regra de pontuação vira `domain/pontuacao.py`; consultas ficam em `services/ranking.py`. |
| `app/bracket.py` | refatorar/fundir | Resolver de bracket vira domínio; sync de palpites vira serviço. |
| `app/standings.py` | mover/refatorar | Classificação por palpite e desempate são domínio puro. |
| `app/chart.py` | refatorar | Payload do gráfico vira serviço pequeno; template SVG gigante descartado. |
| `app/sportsdata.py` | refatorar | Cliente ESPN e aplicação de updates ficam em `services/sincronizacao.py`. |
| `app/recompute_snapshots.py` | mover/refatorar | Vira comando CLI. |
| `app/sync_fixtures.py` | mover/refatorar | Vira comando CLI. |
| `app/seed.py` | mover/refatorar | Seed oficial permanece, com CLI explícita. |
| `app/gen_codes.py`, `seed_fake.py`, `seed_delta_demo.py` | descartar | Scripts temporários/demo; não entram no mínimo operacional. |
| `app/flags.py`, `templates_env.py` | fundir/refatorar | Helpers de flag e Jinja ficam enxutos. |

### Rotas

| Arquivo original | Decisaão | Motivo |
| --- | --- | --- |
| `routers/auth.py` | refatorar | Fluxo essencial permanece; divergência antiga de testes será corrigida. |
| `routers/pages.py` | refatorar | Home, seções, consulta e regulamento continuam com menos dependências externas. |
| `routers/bets.py` | reescrever parcial | Edição permanece, mas menos HTMX e menos partials duplicados. |
| `routers/bracket.py` | fundir | Resumo/completo do palpite entra em rotas menores de viewer/palpites. |
| `routers/compare.py` | refatorar | Mantém geral, 1x1 e mata-mata com tabelas mais simples. |
| `routers/leaderboard.py` | refatorar | Usa servico único de ranking e gráfico simplificado. |
| `routers/live.py` | reescrever parcial | Mantém ao vivo/consolidado sem duplicar lógica de bracket oficial. |
| `routers/admin.py` | refatorar | Mantem seed/sync/admin users; remove endpoints experimentais. |
| `routers/perfil.py`, `viewer.py` | fundir/refatorar | Perfil e visualização de terceiros ficam menores. |

### Templates e static

| Arquivo original | Decisão | Motivo |
| --- | --- | --- |
| `templates/base.html` | reescrever | Navegação e mensagens padronizadas. |
| `templates/index.html` | reescrever | Home operacional para usuário logado. |
| `templates/auth/*` | refatorar | Formulário único de login e primeiro acesso. |
| `templates/bets/aposta.html` | reescrever parcial | Mantém edição de grupos e mata-mata com markup direto. |
| `templates/compare/*` | reescrever | Tabelas simples substituem grids grandes. |
| `templates/leaderboard/leaderboard.html` | reescrever | Ranking, regras e gráfico no mesmo fluxo. |
| `templates/live/live.html` | refatorar | Ao vivo e consolidado usam componentes compactos. |
| `templates/partials/*` | descartar/fundir | Parciais só ficam quando reduzem duplicação real. |
| `public/css/style.css` | reescrever | CSS único menor com tokens, tabelas, forms, cards e nav. |
| `public/js/bracket.js`, `countdown.js`, `ticker.js`, `palpite-download.js` | descartar | Não são essenciais para o mínimo funcional. |
| `public/js/live.js` | reescrever mínimo | Polling/auto-refresh simples se necessário. |
| `public/assets/favicon.*`, `trofeu_copa.png` | manter | Ativos reais do produto. |

### Dados, docs e deploy

| Arquivo original | Decisão | Motivo |
| --- | --- | --- |
| `data/seed/worldcup-2026.json` | manter | Base oficial de times e jogos. |
| `data/roster.json` | descartar | Potencialmente sensível e substituido por admin users. |
| `docs/schema.md`, `architecture.md`, `api-integration.md`, `frontend-style.md` | refatorar | Conteudo útil sera consolidado nos docs novos. |
| `SCORING.md`, `REGULAMENTO.md` | fundir | Regras entram em docs e página de ranking/regulamento. |
| `.env.example`, `pyproject.toml`, `requirements.txt`, `vercel.json` | refatorar | Configuração alvo usa `pyproject.toml`, `.env.example` e CI. |

### Testes

| Arquivo original | Decisão | Motivo |
| --- | --- | --- |
| `tests/test_leaderboard_snapshots.py` | manter/refatorar | Regressão crítica. |
| `tests/test_smoke.py` | refatorar | Fluxos mudaram; preservar cobertura de rotas essenciais. |
| `tests/conftest.py` | refatorar | Isolamento SQLite continua. |

## Arquivos descartados de forma explícita

- Ambientes virtuais: `.venv`, `.venv312`.
- Caches: `.pytest_cache`, `*.egg-info`.
- Banco local real e artefatos em `data/` que não sejam seed público.
- Scripts temporários ou de demo: `seed_fake.py`, `seed_delta_demo.py`, `gen_codes.py`.
- Documentação de ferramenta ou histórica que não orienta manutenção atual.
- CSS e JS acumulados sem tela correspondente no alvo.

## Segunda triagem aplicada

Após comparar novamente rotas e modelos da origem, foram recuperadas features pequenas que tinham valor real e não exigiam copiar os módulos grandes:

- `routers/perfil.py`: mantido como módulo novo e enxuto para troca de nome, nickname e senha.
- `routers/bets.py`: recuperada a intenção de desempate manual de grupos e melhores terceiros.
- `routers/viewer.py`: adicionadas rotas compatíveis `/palpite/{id}/resumo`, `/palpite/{id}/completa` e CSV.
- `routers/live.py`: adicionado detalhe de palpites por jogo de grupo, com visibilidade limitada antes do deadline.

Continuaram fora do alvo:

- Bracket interativo completo com `BetMatch`, por ainda exigir uma modelagem maior para não recriar o acoplamento antigo.
- HTMX/partials do original, porque a versão sem JS cobre o fluxo essencial.
- Admin avançado de edição/exclusão em massa, porque o mínimo operacional já cobre cadastro e liberação pontual.
