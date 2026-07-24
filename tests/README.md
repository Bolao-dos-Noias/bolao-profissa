# Testes

Este documento descreve o que a suíte automatizada cobre hoje e onde estão as principais lacunas, para orientar as próximas issues de testes (ver [Ciclo 3 - #9](https://github.com/Bolao-dos-Noias/bolao-profissa/issues/9) em `docs/issues_milestones.md`).

## Como rodar

```bash
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run pytest
UV_CACHE_DIR=.uv-cache UV_PROJECT_ENVIRONMENT=.venv312 uv run pytest --cov=app --cov-report=term-missing
```

Cobertura total atual: **66%** (17 testes, todos passando). Detalhe por arquivo abaixo.

## Arquivos de teste

- `conftest.py`: fixtures compartilhadas (client de teste, sessão de banco).
- `test_smoke.py`: fluxo HTTP fim-a-fim das páginas e rotas principais.
- `test_snapshots.py`: regras de domínio para ranking e histórico de snapshots.

## O que já está coberto

**Autenticação e onboarding**
- Login com código inválido (`test_login_invalid_code`)
- Primeiro acesso, completar perfil e login subsequente (`test_first_access_complete_profile_and_login`)
- Redirecionamento quando falta perfil ou palpite (`test_no_profile_redirects_to_complete`, `test_no_bet_redirects_to_aposta`, `test_aposta_redirect_sem_login`)

**Palpites**
- Salvar aposta com desempate e ordenação de terceiros (`test_aposta_salva_desempate_e_terceiros`)

**Perfil**
- Atualização de nome (`test_perfil_nome_update`)

**Ranking e live**
- Página de leaderboard ativa (`test_leaderboard_active`)
- Palpites de um jogo ao vivo (`test_live_palpites_do_jogo`)

**Exportação**
- CSV de palpites do usuário (`test_palpite_csv_active`)

**Páginas públicas / smoke**
- Healthcheck, home pública, regulamento, página 404 (`test_healthz`, `test_home_public`, `test_regulamento_active`, `test_404_template_active`)

**Domínio de pontuação e ranking histórico**
- Sincronização incremental de snapshots ignorando jogos ao vivo (`test_sync_snapshots_are_incremental_and_ignore_live_matches`)
- Recompute reparando histórico existente de forma incremental (`test_recompute_snapshots_repairs_existing_history_incrementally`)
- Pontuação de R32/top2 no fechamento de grupo e terceiros após todos os grupos (`test_recompute_awards_r32_top2_on_group_close_and_thirds_after_all_groups`)

## O que falta testar

Lacunas identificadas pela cobertura por arquivo (`uv run pytest --cov=app --cov-report=term-missing`), da mais crítica para a menos crítica:

| Módulo | Cobertura | Falta testar |
| --- | --- | --- |
| `app/services/seed.py` | 20% | Fluxo completo de `seed()` (hoje só é exercitado indiretamente); casos de re-seed com `force=True`. |
| `app/cli/seed.py`, `app/cli/sync_fixtures.py` | 0% | Nenhum teste chama esses entrypoints de CLI diretamente. |
| `app/routers/live.py` | 38% | `/ao-vivo`, `/ao-vivo/consolidado` e `/ao-vivo/consolidado/completo` (só `palpites_do_jogo` tem teste). |
| `app/routers/compare.py` | 48% | Os três comparativos (`geral`, `1x1`, `mata-mata`) não têm teste algum. |
| `app/routers/perfil.py` | 50% | Troca de nickname e de senha (`senha_save`), e os casos de erro (senha atual incorreta, nickname duplicado). |
| `app/routers/viewer.py` | 51% | Visualização de palpite de outro usuário (`palpite_publico`), controle de privacidade (`_can_view`), rotas de compatibilidade (`/palpite/{user_id}/...`). |
| `app/services/sincronizacao.py` | 51% | `sync_once` fim-a-fim contra payload real/mock da ESPN, resolução de times por código/nome, cálculo de relógio ao vivo. |
| `app/routers/bets.py` | 55% | `post_group_pick` e `post_ko_stage` (só o fluxo combinado de desempate/terceiros está coberto), validação de payload inválido. |
| `app/routers/pages.py` | 58% | Rotas estáticas restantes além da home. |
| `app/routers/leaderboard.py` | 66% | Montagem do payload do gráfico (`_chart_payload`, já identificado como complexo em `docs/metricas.md`). |
| `app/routers/admin.py` | 43% | `admin_seed`/`admin_sync` com token válido e inválido, criação de usuário (`users_create`), desbloqueio de usuário (`users_unlock`). Área administrativa é a mais crítica sem cobertura. |
| `app/deps.py`, `app/db.py`, `app/auth.py` | 71-75% | Caminhos de erro/exceção (sessão inválida, usuário não encontrado). |
| `app/domain/pontuacao.py`, `app/domain/classificacao.py` | 92-95% | Poucos casos de borda pontuais faltando (ver linhas em `--cov-report=term-missing`); domínio já é a área mais bem coberta. |

Prioridade sugerida: **admin** (rotas administrativas sem nenhum teste de autorização) e **sincronização ESPN** (integração externa), por serem os pontos de maior risco operacional hoje.
