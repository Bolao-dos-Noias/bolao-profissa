# Arquitetura

## Camadas

- `app/routers`: entrada HTTP, validacao leve e renderizacao de templates.
- `app/services`: casos de uso, consultas coordenadas e transacoes.
- `app/domain`: regras puras de classificacao, bracket, pontuacao e snapshots.
- `app/repositories`: consultas persistentes compartilhadas quando reduzem duplicacao.
- `app/cli`: comandos operacionais para seed, sync e recompute.
- `app/templates`: Jinja com logica minima.
- `app/static`: CSS e JavaScript reduzidos ao necessario.

```mermaid
flowchart TD
    Client["Navegador"] --> Routers["app/routers\nHTTP + validacao leve"]
    Routers --> Services["app/services\ncasos de uso e transacoes"]
    Services --> Domain["app/domain\nregras puras: pontuacao, classificacao, snapshots"]
    Services --> Repositories["app/repositories\nconsultas compartilhadas"]
    Services --> DB[("Banco\nSQLite / Turso libsql")]
    Repositories --> DB
    CLI["app/cli\nseed, sync, recompute"] --> Services
    Routers --> Templates["app/templates + app/static\nJinja / CSS / JS"]
    External["API ESPN"] -.sincronizacao.-> CLI
```

## Fonte de verdade da pontuacao

`app/domain/pontuacao.py` define pesos, ordenacao, desempates e serializacao de snapshots. `app/services/ranking.py` converte dados persistidos para essa regra. Ranking, comparativos, live e recompute consomem o mesmo servico.

## Banco

O alvo preserva SQLModel, SQLite local e Turso/libsql. Dados sensiveis ficam fora do Git e sao configurados por `.env`.

## Modelagem de dados

Todas as tabelas sao definidas em `app/models.py` com SQLModel. Nao ha um unico agregado central: `User`, `Team` e `Match` sao as entidades base, e cada tipo de palpite tem sua propria tabela normalizada.

### Entidades base

#### `User` (`users`)

```mermaid
erDiagram
    USER {
        int id PK
        string email UK
        string username UK
        string nickname UK
        string nome_completo
        string roster_slug UK
        string invite_code UK
        string password_hash
        bool is_admin
        datetime edit_unlock_until
        datetime created_at
    }
```

Participante do bolao. `nickname` e o identificador publico (usado em URLs de palpite/comparacao). `email`, `username`, `roster_slug` e `invite_code` sao opcionais, suportando os diferentes fluxos de onboarding. `edit_unlock_until` reabre a edicao de palpites apos o fechamento geral para um usuario especifico.

#### `Team` (`teams`)

```mermaid
erDiagram
    TEAM {
        int id PK
        string name_pt
        string fifa_code UK
        string iso2
        string group_letter
    }
```

Selecao da Copa. `fifa_code` e a chave natural usada para casar com a API da ESPN durante a sincronizacao; `group_letter` associa o time a um grupo (A-H).

#### `Match` (`matches`)

```mermaid
erDiagram
    MATCH {
        int id PK
        string external_id UK
        string stage
        string group_letter
        int match_no
        int home_team_id FK
        int away_team_id FK
        string slot_home
        string slot_away
        datetime kickoff_utc
        string venue
        string status
        int home_score
        int away_score
        string result
        datetime last_synced_at
        string live_clock
        int live_period
    }
```

Partida, tanto de grupo quanto de mata-mata. `stage` distingue `GROUP` de `R32`, `R16`, `QF`, `SF`, `F` e `CHAMPION`; `group_letter`/`match_no` so fazem sentido na fase de grupos. `home_team_id`/`away_team_id` ficam nulos antes da definicao do chaveamento, por isso `slot_home`/`slot_away` guardam o placeholder textual (ex.: "1o Grupo A"). `external_id` e a chave de casamento com a ESPN. `status`, `*_score`, `result` e `live_*` sao atualizados por `app/services/sincronizacao.py`.

### Palpites (uma tabela por tipo de aposta)

Cada fase do bolao tem regra de pontuacao propria (`app/domain/pontuacao.py`) e granularidade diferente: grupo e por jogo, desempate e por grupo inteiro, terceiros e global, mata-mata e por fase ou por confronto. Por isso cada tipo de palpite vive em sua propria tabela.

#### `BetGroup` (`bets_group`)

```mermaid
erDiagram
    BET_GROUP {
        int id PK
        int user_id FK
        int match_id FK
        string pick
        datetime updated_at
    }
```

Palpite de resultado (`pick` em `HOME`/`DRAW`/`AWAY`) para um jogo de grupo. Unicidade composta em `(user_id, match_id)`.

#### `BetTieBreak` (`bets_tie_break`)

```mermaid
erDiagram
    BET_TIE_BREAK {
        int id PK
        int user_id FK
        string group_letter
        string ordered_team_ids
        datetime updated_at
    }
```

Desempate de classificacao dentro de um grupo; `ordered_team_ids` guarda a ordem completa dos times do grupo serializada como string. Unicidade composta em `(user_id, group_letter)`.

#### `BetThirdsOrder` (`bets_thirds_order`)

```mermaid
erDiagram
    BET_THIRDS_ORDER {
        int user_id "PK, FK"
        string ordered_team_ids
        datetime updated_at
    }
```

Ordenacao dos melhores terceiros colocados entre todos os grupos. A chave primaria e o proprio `user_id` (um registro por usuario, nao por grupo).

#### `BetKnockout` (`bets_knockout`)

```mermaid
erDiagram
    BET_KNOCKOUT {
        int id PK
        int user_id FK
        string stage
        int team_id FK
        datetime updated_at
    }
```

Palpite de quais times avancam em uma fase de mata-mata. Unicidade composta em `(user_id, stage, team_id)` - o conjunto de linhas com o mesmo `(user_id, stage)` representa os classificados escolhidos para aquela fase.

#### `BetMatch` (`bets_match`)

```mermaid
erDiagram
    BET_MATCH {
        int id PK
        int user_id FK
        int match_id FK
        int winner_team_id FK
        datetime updated_at
    }
```

Palpite de vencedor de um confronto de mata-mata ja definido. Unicidade composta em `(user_id, match_id)`.

### Historico e configuracao

#### `LeaderboardSnapshot` (`leaderboard_snapshots`)

```mermaid
erDiagram
    LEADERBOARD_SNAPSHOT {
        int id PK
        datetime captured_at
        int match_id FK
        string ordering
    }
```

Foto do ranking em um instante, tirada a cada jogo processado (`match_id` aponta para o jogo que disparou a atualizacao). `ordering` serializa posicoes e pontuacao de todos os usuarios naquele momento (`serialize_snapshot_ordering`/`parse_snapshot` em `app/services/ranking.py`), permitindo montar o grafico de evolucao do ranking sem recalcular tudo a cada leitura.

#### `Setting` (`settings`)

```mermaid
erDiagram
    SETTING {
        string key PK
        string value
    }
```

Tabela chave-valor generica para configuracao operacional persistida (ex.: flags de estado do workflow), separada das variaveis de `.env`.

### Relacionamentos

Visao geral de como as entidades acima se conectam (campos completos de cada uma estao nos diagramas por entidade anteriores):

```mermaid
erDiagram
    USER ||--o{ BET_GROUP : aposta
    USER ||--o{ BET_TIE_BREAK : aposta
    USER ||--|| BET_THIRDS_ORDER : aposta
    USER ||--o{ BET_KNOCKOUT : aposta
    USER ||--o{ BET_MATCH : aposta
    TEAM ||--o{ MATCH : "manda/visita"
    TEAM ||--o{ BET_KNOCKOUT : "e o time escolhido"
    TEAM ||--o{ BET_MATCH : "e o vencedor escolhido"
    MATCH ||--o{ BET_GROUP : recebe
    MATCH ||--o{ BET_MATCH : recebe
    MATCH ||--o{ LEADERBOARD_SNAPSHOT : origina
```

Nao ha cascade delete configurado: a integridade entre `users`/`teams`/`matches` e as tabelas de aposta e responsabilidade da camada de servico (`app/services/palpites.py`), que sempre escreve/atualiza pelo par de chaves unico em vez de duplicar linhas.

