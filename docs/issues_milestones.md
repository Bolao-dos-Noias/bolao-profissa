# Issues e Milestones

## Milestone 0 - Inventario e Planejamento

- #1 `docs: registrar inventario do repositorio original` - Gabriel
- #2 `docs: definir arquitetura alvo` - Gabriel
- #3 `docs: mapear features essenciais e criterios de aceite` - Nicolas

## Milestone 1 - Bootstrap Limpo

- #4 `chore: inicializar estrutura limpa do projeto` - Gabriel
- #5 `chore: configurar ruff pylint radon pytest` - Gabriel
- #6 `ci: adicionar pipeline de qualidade` - Gabriel

## Milestone 2 - Dominio e Pontuacao

- #7 `refactor: criar dominio de pontuacao` - Caio
- #8 `test: cobrir grupos zebras e mata-mata` - Caio
- #9 `refactor: unificar snapshots e ranking` - Gabriel

## Milestone 3 - Dados API e Persistencia

- #10 `refactor: isolar sincronizacao ESPN` - Caio
- #11 `chore: criar cli de seed sync e recompute` - Caio
- #12 `docs: documentar operacao local e producao` - Nicolas

## Milestone 4 - Frontend Enxuto

- #13 `refactor: simplificar templates de palpites` - Felipe
- #14 `refactor: consolidar CSS base` - Felipe
- #15 `feat: organizar navegacao principal` - Felipe

## Milestone 5 - Ranking Snapshots Historico

- #16 `test: cobrir recompute incremental` - Caio
- #17 `refactor: separar payload do grafico` - Gabriel
- #18 `docs: explicar historico de snapshots` - Nicolas

## Milestone 6 - Polimento Metricas Entrega

- #19 `docs: registrar metricas finais` - Gabriel
- #20 `fix: reduzir complexidade dos modulos criticos` - todos
- #21 `docs: escrever relatorio final` - Nicolas

## Rodada 2 - Lacunas da Referencia

- #22 `feat: recuperar desempates e terceiros dos palpites` - Caio
- #23 `feat: recuperar perfil e exportacao csv de palpites` - Gabriel
- #24 `refactor: expor fluxos recuperados na interface minima` - Felipe
- #25 `docs: atualizar relatorio de triagem e metricas` - Nicolas

## Ciclos 1-4 - Fechar lacunas frente ao repositorio de referencia

Baseado no levantamento de `faltantes.md` (comparacao com o repositorio de referencia `bolao-dos-noia`). Estes 4 ciclos sao Milestones reais, ja criadas no GitHub (`Bolao-dos-Noias/bolao-profissa`), substituindo o antigo milestone unico "Ciclo 0 - Inventario e Planejamento" (fechado). Cada Milestone agrupa um tema e cada issue tem responsavel (assignee), reviewer, labels e criterios de aceite.

As issues #3 e #4 ja existiam no GitHub (criadas antes deste levantamento, dentro do extinto "Ciclo 0") e foram reaproveitadas - apenas movidas de milestone e, no caso da #4, com criterios de aceite atualizados - em vez de duplicadas.

### [Ciclo 1 - Fundamentos e Onboarding](https://github.com/Bolao-dos-Noias/bolao-profissa/milestone/2)

- [#3](https://github.com/Bolao-dos-Noias/bolao-profissa/issues/3) `docs: documentar onboarding e README do projeto` - Nicolas
- [#4](https://github.com/Bolao-dos-Noias/bolao-profissa/issues/4) `ci: reforcar pipeline de qualidade` - Gabriel
- [#5](https://github.com/Bolao-dos-Noias/bolao-profissa/issues/5) `chore: criar seed e fixtures operacionais para desenvolvimento` - Caio

### [Ciclo 2 - Experiencia do Produto](https://github.com/Bolao-dos-Noias/bolao-profissa/milestone/3)

- [#6](https://github.com/Bolao-dos-Noias/bolao-profissa/issues/6) `feat: implementar fluxo de bracket e mata-mata` - Caio
- [#7](https://github.com/Bolao-dos-Noias/bolao-profissa/issues/7) `refactor: melhorar experiencia de palpites e navegacao` - Felipe
- [#8](https://github.com/Bolao-dos-Noias/bolao-profissa/issues/8) `refactor: polir telas de live, compare e ranking` - Felipe

### [Ciclo 3 - Operacao, Regras e Qualidade](https://github.com/Bolao-dos-Noias/bolao-profissa/milestone/4)

- [#9](https://github.com/Bolao-dos-Noias/bolao-profissa/issues/9) `test: expandir cobertura para fluxos criticos` - Caio
- [#10](https://github.com/Bolao-dos-Noias/bolao-profissa/issues/10) `docs: documentar regras de pontuacao e regulamento` - Nicolas
- [#11](https://github.com/Bolao-dos-Noias/bolao-profissa/issues/11) `refactor: melhorar fluxo de perfil e administracao` - Gabriel

### [Ciclo 4 - Refinamento Tecnico e Visual](https://github.com/Bolao-dos-Noias/bolao-profissa/milestone/5)

- [#12](https://github.com/Bolao-dos-Noias/bolao-profissa/issues/12) `refactor: revisar metricas, performance e manutencao tecnica` - Gabriel
- [#13](https://github.com/Bolao-dos-Noias/bolao-profissa/issues/13) `chore: polir visual e assets do projeto` - Felipe

### Detalhamento das issues

---

#### #3 - docs: documentar onboarding e README do projeto

**Milestone:** Ciclo 1 - Fundamentos e Onboarding
**Responsavel:** Nicolas
**Reviewer:** Gabriel
**Labels:** documentation

**Descricao**
Consolidar a documentacao inicial do projeto para facilitar a entrada de novos participantes e padronizar o fluxo de contribuicao.

**Criterios de aceite**
- [ ] README com visao do produto, stack, setup local e fluxo de contribuicao
- [ ] Links para documentacao complementar e backlog
- [ ] Texto claro e consistente com o estado atual do projeto

**Arquivos-alvo**
- README.md
- docs/guia_contribuicao.md
- docs/arquitetura.md

---

#### #4 - ci: reforcar pipeline de qualidade

**Milestone:** Ciclo 1 - Fundamentos e Onboarding
**Responsavel:** Gabriel
**Reviewer:** Gabriel
**Labels:** ci/cd, quality

**Descricao**
O pipeline em `.github/workflows/ci.yml` ja roda ruff, pytest, pylint e radon a cada PR. Falta fechar o que garante que ele seja, de fato, um portao de qualidade: cobertura minima obrigatoria, visibilidade do status no README e protecao de branch exigindo o check antes do merge.

**Criterios de aceite**
- [ ] `pytest --cov` com limite minimo de cobertura que falha o build abaixo do threshold
- [ ] Badge de status do CI no README
- [ ] Branch protection do `main` exigindo o check de CI antes do merge (configuracao em Settings > Branches)

**Arquivos-alvo**
- .github/workflows/ci.yml
- README.md
- pyproject.toml

---

#### #5 - chore: criar seed e fixtures operacionais para desenvolvimento

**Milestone:** Ciclo 1 - Fundamentos e Onboarding
**Responsavel:** Caio
**Reviewer:** Gabriel
**Labels:** chore, backend

**Descricao**
Facilitar a execucao local com dados realistas e cenarios pre-populados para desenvolvimento e testes.

**Criterios de aceite**
- [ ] Comandos para popular dados de exemplo
- [ ] Seed com times, partidas e usuarios de teste
- [ ] Fluxo simples para reproduzir cenarios de uso

**Arquivos-alvo**
- app/cli/
- data/seed/
- app/services/

---

#### #6 - feat: implementar fluxo de bracket e mata-mata

**Milestone:** Ciclo 2 - Experiencia do Produto
**Responsavel:** Caio
**Reviewer:** Gabriel
**Labels:** feature, backend

**Descricao**
Maior lacuna identificada em `faltantes.md` frente ao repositorio de referencia: adicionar o fluxo de bracket e mata-mata com interface e logica compativel com as regras do bolao.

**Criterios de aceite**
- [ ] Interface para visualizacao do bracket
- [ ] Persistencia e calculo compativel com a logica atual
- [ ] Fluxo navegavel e consistente com o restante do produto

**Arquivos-alvo**
- app/routers/
- app/templates/
- app/services/
- app/domain/

---

#### #7 - refactor: melhorar experiencia de palpites e navegacao

**Milestone:** Ciclo 2 - Experiencia do Produto
**Responsavel:** Felipe
**Reviewer:** Gabriel
**Labels:** frontend, ux

**Descricao**
Tornar o fluxo de palpites, ranking e consulta mais claro e consistente para o usuario.

**Criterios de aceite**
- [ ] Menus e links mais claros
- [ ] Fluxo consistente entre aposta e confirmacao
- [ ] Reducao de pontos de confusao na navegacao

**Arquivos-alvo**
- app/templates/
- app/static/css/
- app/routers/

---

#### #8 - refactor: polir telas de live, compare e ranking

**Milestone:** Ciclo 2 - Experiencia do Produto
**Responsavel:** Felipe
**Reviewer:** Gabriel
**Labels:** frontend, enhancement

**Descricao**
Deixar as telas principais mais proximas do visual e da usabilidade esperados para o bolao.

**Criterios de aceite**
- [ ] Interface mais consistente com o produto
- [ ] Componentes reutilizaveis e menos duplicacao de HTML/CSS
- [ ] Melhor experiencia visual nas telas principais

**Arquivos-alvo**
- app/templates/live/
- app/templates/compare/
- app/templates/leaderboard/
- app/static/css/

---

#### #9 - test: expandir cobertura para fluxos criticos

**Milestone:** Ciclo 3 - Operacao, Regras e Qualidade
**Responsavel:** Caio
**Reviewer:** Gabriel
**Labels:** tests, backend

**Descricao**
Cobrir os cenarios de autenticacao, workflow, palpites, ranking e exportacao com testes automatizados.

**Criterios de aceite**
- [ ] Testes para login e onboarding
- [ ] Testes para fluxos de palpites e ranking
- [ ] Testes para exportacao e regras principais de pontuacao

**Arquivos-alvo**
- tests/
- app/services/
- app/domain/

---

#### #10 - docs: documentar regras de pontuacao e regulamento

**Milestone:** Ciclo 3 - Operacao, Regras e Qualidade
**Responsavel:** Nicolas
**Reviewer:** Gabriel
**Labels:** documentation, rules

**Descricao**
Deixar as regras do bolao explicitas e faceis de revisar para participantes e contribuidores.

**Criterios de aceite**
- [ ] Documento com regras de pontuacao, desempates e fluxo de disputa
- [ ] Referencia acessivel para participantes e contribuidores
- [ ] Conteudo alinhado com a implementacao atual

**Arquivos-alvo**
- docs/
- app/domain/
- app/services/

---

#### #11 - refactor: melhorar fluxo de perfil e administracao

**Milestone:** Ciclo 3 - Operacao, Regras e Qualidade
**Responsavel:** Gabriel
**Reviewer:** Gabriel
**Labels:** enhancement, backend

**Descricao**
Reforcar os fluxos de perfil, seguranca e operacoes administrativas para reduzir atritos operacionais.

**Criterios de aceite**
- [ ] Perfil mais completo e consistente
- [ ] Administracao com menos friccao para operacoes do bolao
- [ ] Fluxos de acesso e atualizacao mais intuitivos

**Arquivos-alvo**
- app/routers/perfil.py
- app/routers/admin.py
- app/templates/perfil/
- app/templates/admin/

---

#### #12 - refactor: revisar metricas, performance e manutencao tecnica

**Milestone:** Ciclo 4 - Refinamento Tecnico e Visual
**Responsavel:** Gabriel
**Reviewer:** Gabriel
**Labels:** refactor, quality

**Descricao**
Reduzir complexidade e melhorar a manutenibilidade do codigo em pontos criticos do projeto.

**Criterios de aceite**
- [ ] Codigo com menor complexidade em modulos criticos
- [ ] Documentacao atualizada com decisoes de arquitetura
- [ ] Melhoria percebida na facilidade de manutencao

**Arquivos-alvo**
- app/domain/
- app/services/
- app/routers/
- docs/arquitetura.md

---

#### #13 - chore: polir visual e assets do projeto

**Milestone:** Ciclo 4 - Refinamento Tecnico e Visual
**Responsavel:** Felipe
**Reviewer:** Gabriel
**Labels:** frontend, design

**Descricao**
Alinhar a identidade visual do projeto e melhorar a experiencia visual geral do bolao.

**Criterios de aceite**
- [ ] Assets reutilizados de forma consistente
- [ ] CSS e templates mais enxutos
- [ ] Melhor consistencia visual nas telas principais

**Arquivos-alvo**
- app/static/assets/
- app/static/css/
- app/templates/

---

### Labels padronizados

Reaproveitando o que ja foi usado nos ciclos anteriores. Criar as que ainda nao existirem em Settings > Labels antes de abrir as issues do Ciclo 3.

| Label | Uso |
| --- | --- |
| `feature` | Nova funcionalidade de produto |
| `enhancement` | Melhoria de algo que ja existe |
| `refactor` | Mudanca interna sem alterar comportamento externo |
| `documentation` | Documentacao (README, docs/, regulamento) |
| `tests` | Testes automatizados |
| `ci/cd` | Pipeline e automacao de qualidade |
| `quality` | Metricas de qualidade (cobertura, lint, complexidade) |
| `chore` | Tarefa operacional sem impacto direto de produto |
| `backend` | Dominio, servicos, persistencia, rotas |
| `frontend` | Templates, CSS, navegacao |
| `ux` | Experiencia e fluxo de uso |
| `design` | Identidade visual e assets |
| `rules` | Regras de pontuacao e regulamento do bolao |

### Ordem dos ciclos

1. Ciclo 1 - Fundamentos e onboarding
2. Ciclo 2 - Experiencia do produto
3. Ciclo 3 - Operacao e documentacao
4. Ciclo 4 - Refinamento tecnico e visual
