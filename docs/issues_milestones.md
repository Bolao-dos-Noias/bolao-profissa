# Issues e Milestones

## Milestone 0 - Inventário e Planejamento

- #1 `docs: registrar inventário do repositório original` - Gabriel
- #2 `docs: definir arquitetura alvo` - Gabriel
- #3 `docs: mapear features essenciais e critérios de aceite` - Nicolas

## Milestone 1 - Bootstrap Limpo

- #4 `chore: inicializar estrutura limpa do projeto` - Gabriel
- #5 `chore: configurar ruff pylint radon pytest` - Gabriel
- #6 `ci: adicionar pipeline de qualidade` - Gabriel

## Milestone 2 - Domínio e Pontuaçío

- #7 `refactor: criar dominio de pontuação` - Caio
- #8 `test: cobrir grupos zebras e mata-mata` - Caio
- #9 `refactor: unificar snapshots e ranking` - Gabriel

## Milestone 3 - Dados API e Persistencia

- #10 `refactor: isolar sincronização ESPN` - Caio
- #11 `chore: criar cli de seed sync e recompute` - Caio
- #12 `docs: documentar operacao local e produção` - Nicolas

## Milestone 4 - Frontend Enxuto

- #13 `refactor: simplificar templates de palpites` - Felipe
- #14 `refactor: consolidar CSS base` - Felipe
- #15 `feat: organizar navegação principal` - Felipe

## Milestone 5 - Ranking Snapshots Histórico

- #16 `test: cobrir recompute incremental` - Caio
- #17 `refactor: separar payload do gráfico` - Gabriel
- #18 `docs: explicar histórico de snapshots` - Nicolas

## Milestone 6 - Polimento Métricas Entrega

- #19 `docs: registrar métricas finais` - Gabriel
- #20 `fix: reduzir complexidade dos módulos críticos` - todos
- #21 `docs: escrever relatório final` - Nicolas

## Rodada 2 - Lacunas da Referência

- #22 `feat: recuperar desempates e terceiros dos palpites` - Caio
- #23 `feat: recuperar perfil e exportação csv de palpites` - Gabriel
- #24 `refactor: expor fluxos recuperados na interface mínima` - Felipe
- #25 `docs: atualizar relatório de triagem e métricas` - Nicolas

## Ciclos 1-4 - Fechar lacunas frente ao repositório de referência

Baseado na comparação com o repositório de referência `bolao-dos-noia`. Estes 4 ciclos são Milestones reais, já criadas no GitHub (`Bolao-dos-Noias/bolao-profissa`), substituindo o antigo milestone único "Ciclo 0 - Inventario e Planejamento" (fechado). Cada Milestone agrupa um tema e cada issue tem responsável (assignee), reviewer, labels e critérios de aceite.

As issues #3 e #4 já existiam no GitHub (criadas antes deste levantamento, dentro do extinto "Ciclo 0") e foram reaproveitadas - apenas movidas de milestone e, no caso da #4, com critérios de aceite atualizados - em vez de duplicadas.

### [Ciclo 1 - Fundamentos e Onboarding](https://github.com/Bolao-dos-Noias/bolao-profissa/milestone/2)

- [#3](https://github.com/Bolao-dos-Noias/bolao-profissa/issues/3) `docs: documentar onboarding e README do projeto` - Nicolas
- [#4](https://github.com/Bolao-dos-Noias/bolao-profissa/issues/4) `ci: reforçar pipeline de qualidade` - Gabriel
- [#5](https://github.com/Bolao-dos-Noias/bolao-profissa/issues/5) `chore: criar seed e fixtures operacionais para desenvolvimento` - Caio

### [Ciclo 2 - Experiência do Produto](https://github.com/Bolao-dos-Noias/bolao-profissa/milestone/3)

- [#6](https://github.com/Bolao-dos-Noias/bolao-profissa/issues/6) `feat: implementar fluxo de bracket e mata-mata` - Caio
- [#7](https://github.com/Bolao-dos-Noias/bolao-profissa/issues/7) `refactor: melhorar experiencia de palpites e navegação` - Felipe
- [#8](https://github.com/Bolao-dos-Noias/bolao-profissa/issues/8) `refactor: polir telas de live, compare e ranking` - Felipe

### [Ciclo 3 - Operação, Regras e Qualidade](https://github.com/Bolao-dos-Noias/bolao-profissa/milestone/4)

- [#9](https://github.com/Bolao-dos-Noias/bolao-profissa/issues/9) `test: expandir cobertura para fluxos críticos` - Caio
- [#10](https://github.com/Bolao-dos-Noias/bolao-profissa/issues/10) `docs: documentar regras de pontuação e regulamento` - Nicolas
- [#11](https://github.com/Bolao-dos-Noias/bolao-profissa/issues/11) `refactor: melhorar fluxo de perfil e administração` - Gabriel

### [Ciclo 4 - Refinamento Técnico e Visual](https://github.com/Bolao-dos-Noias/bolao-profissa/milestone/5)

- [#12](https://github.com/Bolao-dos-Noias/bolao-profissa/issues/12) `refactor: revisar métricas, performance e manutenção técnica` - Gabriel
- [#13](https://github.com/Bolao-dos-Noias/bolao-profissa/issues/13) `chore: polir visual e assets do projeto` - Felipe

### Detalhamento das issues

---

#### #3 - docs: documentar onboarding e README do projeto

**Milestone:** Ciclo 1 - Fundamentos e Onboarding
**Responsável:** Nicolas
**Reviewer:** Gabriel
**Labels:** documentation

**Descrição**
Consolidar a documentação inicial do projeto para facilitar a entrada de novos participantes e padronizar o fluxo de contribuição.

**Critérios de aceite**
- [ ] README com visão do produto, stack, setup local e fluxo de contribuição
- [ ] Links para documentação complementar e backlog
- [ ] Texto claro e consistente com o estado atual do projeto

**Arquivos-alvo**
- README.md
- docs/guia_contribuicao.md
- docs/arquitetura.md

---

#### #4 - ci: reforçar pipeline de qualidade

**Milestone:** Ciclo 1 - Fundamentos e Onboarding
**Responsável:** Gabriel
**Reviewer:** Gabriel
**Labels:** ci/cd, quality

**Descrição**
O pipeline em `.github/workflows/ci.yml` já roda ruff, pytest, pylint e radon a cada PR. Falta fechar o que garante que ele seja, de fato, um portao de qualidade: cobertura mínima obrigatória, visibilidade do status no README e proteção de branch exigindo o check antes do merge.

**Critérios de aceite**
- [ ] `pytest --cov` com limite mínimo de cobertura que falha o build abaixo do threshold
- [ ] Badge de status do CI no README
- [ ] Branch protection do `main` exigindo o check de CI antes do merge (configuração em Settings > Branches)

**Arquivos-alvo**
- .github/workflows/ci.yml
- README.md
- pyproject.toml

---

#### #5 - chore: criar seed e fixtures operacionais para desenvolvimento

**Milestone:** Ciclo 1 - Fundamentos e Onboarding
**Responsável:** Caio
**Reviewer:** Gabriel
**Labels:** chore, backend

**Descrição**
Facilitar a execução local com dados realistas e cenarios pré-populados para desenvolvimento e testes.

**Critérios de aceite**
- [ ] Comandos para popular dados de exemplo
- [ ] Seed com times, partidas e usuários de teste
- [ ] Fluxo simples para reproduzir cenários de uso

**Arquivos-alvo**
- app/cli/
- data/seed/
- app/services/

---

#### #6 - feat: implementar fluxo de bracket e mata-mata

**Milestone:** Ciclo 2 - Experiência do Produto
**Responsável:** Caio
**Reviewer:** Gabriel
**Labels:** feature, backend

**Descrição**
Maior lacuna frente ao repositório de referência: adicionar o fluxo de bracket e mata-mata com interface e lógica compatível com as regras do bolão.

**Critérios de aceite**
- [ ] Interface para visualização do bracket
- [ ] Persistência e cálculo compatível com a lógica atual
- [ ] Fluxo navegável e consistente com o restante do produto

**Arquivos-alvo**
- app/routers/
- app/templates/
- app/services/
- app/domain/

---

#### #7 - refactor: melhorar experiência de palpites e navegação

**Milestone:** Ciclo 2 - Experiência do Produto
**Responsável:** Felipe
**Reviewer:** Gabriel
**Labels:** frontend, ux

**Descrição**
Tornar o fluxo de palpites, ranking e consulta mais claro e consistente para o usuário.

**Critérios de aceite**
- [ ] Menus e links mais claros
- [ ] Fluxo consistente entre aposta e confirmação
- [ ] Redução de pontos de confusão na navegação

**Arquivos-alvo**
- app/templates/
- app/static/css/
- app/routers/

---

#### #8 - refactor: polir telas de live, compare e ranking

**Milestone:** Ciclo 2 - Experiência do Produto
**Responsável:** Felipe
**Reviewer:** Gabriel
**Labels:** frontend, enhancement

**Descrição**
Deixar as telas principais mais próximas do visual e da usabilidade esperados para o bolão.

**Critérios de aceite**
- [ ] Interface mais consistente com o produto
- [ ] Componentes reutilizáveis e menos duplicacao de HTML/CSS
- [ ] Melhor experiência visual nas telas principais

**Arquivos-alvo**
- app/templates/live/
- app/templates/compare/
- app/templates/leaderboard/
- app/static/css/

---

#### #9 - test: expandir cobertura para fluxos criticos

**Milestone:** Ciclo 3 - Operação, Regras e Qualidade
**Responsável:** Caio
**Reviewer:** Gabriel
**Labels:** tests, backend

**Descrição**
Cobrir os cenários de autenticação, workflow, palpites, ranking e exportação com testes automatizados.

**Critérios de aceite**
- [ ] Testes para login e onboarding
- [ ] Testes para fluxos de palpites e ranking
- [ ] Testes para exportacao e regras principais de pontuação

**Arquivos-alvo**
- tests/
- app/services/
- app/domain/

---

#### #10 - docs: documentar regras de pontuação e regulamento

**Milestone:** Ciclo 3 - Operação, Regras e Qualidade
**Responsável:** Nicolas
**Reviewer:** Gabriel
**Labels:** documentation, rules

**Descrição**
Deixar as regras do bolão explícitas e fáceis de revisar para participantes e contribuidores.

**Critérios de aceite**
- [ ] Documento com regras de pontuação, desempates e fluxo de disputa
- [ ] Referência acessível para participantes e contribuidores
- [ ] Conteúdo alinhado com a implementação atual

**Arquivos-alvo**
- docs/
- app/domain/
- app/services/

---

#### #11 - refactor: melhorar fluxo de perfil e administração

**Milestone:** Ciclo 3 - Operação, Regras e Qualidade
**Responsável:** Gabriel
**Reviewer:** Gabriel
**Labels:** enhancement, backend

**Descrição**
Reforcar os fluxos de perfil, segurança e operações administrativas para reduzir atritos operacionais.

**Critérios de aceite**
- [ ] Perfil mais completo e consistente
- [ ] Administração com menos fricção para operações do bolão
- [ ] Fluxos de acesso e atualização mais intuitivos

**Arquivos-alvo**
- app/routers/perfil.py
- app/routers/admin.py
- app/templates/perfil/
- app/templates/admin/

---

#### #12 - refactor: revisar métricas, performance e manutenção técnica

**Milestone:** Ciclo 4 - Refinamento Técnico e Visual
**Responsável:** Gabriel
**Reviewer:** Gabriel
**Labels:** refactor, quality

**Descrição**
Reduzir complexidade e melhorar a manutenibilidade do codigo em pontos críticos do projeto.

**Critérios de aceite**
- [ ] Código com menor complexidade em modulos críticos
- [ ] Documentação atualizada com decisões de arquitetura
- [ ] Melhoria percebida na facilidade de manutenção

**Arquivos-alvo**
- app/domain/
- app/services/
- app/routers/
- docs/arquitetura.md

---

#### #13 - chore: polir visual e assets do projeto

**Milestone:** Ciclo 4 - Refinamento Tecnico e Visual
**Responsável:** Felipe
**Reviewer:** Gabriel
**Labels:** frontend, design

**Descrição**
Alinhar a identidade visual do projeto e melhorar a experiência visual geral do bolão.

**Critérios de aceite**
- [ ] Assets reutilizados de forma consistente
- [ ] CSS e templates mais enxutos
- [ ] Melhor consistência visual nas telas principais

**Arquivos-alvo**
- app/static/assets/
- app/static/css/
- app/templates/

---

### Labels padronizados

Reaproveitando o que já foi usado nos ciclos anteriores. Criar as que ainda não existirem em Settings > Labels antes de abrir as issues do Ciclo 3.

| Label | Uso |
| --- | --- |
| `feature` | Nova funcionalidade de produto |
| `enhancement` | Melhoria de algo que já existe |
| `refactor` | Mudança interna sem alterar comportamento externo |
| `documentation` | Documentação (README, docs/, regulamento) |
| `tests` | Testes automatizados |
| `ci/cd` | Pipeline e automação de qualidade |
| `quality` | Métricas de qualidade (cobertura, lint, complexidade) |
| `chore` | Tarefa operacional sem impacto direto de produto |
| `backend` | Domínio, serviços, persistência, rotas |
| `frontend` | Templates, CSS, navegação |
| `ux` | Experiência e fluxo de uso |
| `design` | Identidade visual e assets |
| `rules` | Regras de pontuação e regulamento do bolão |

### Ordem dos ciclos

1. Ciclo 1 - Fundamentos e onboarding
2. Ciclo 2 - Experiência do produto
3. Ciclo 3 - Operação e documentação
4. Ciclo 4 - Refinamento técnico e visual
