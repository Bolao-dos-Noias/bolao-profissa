# Deploy em producao

Este documento descreve a topologia de producao, o procedimento de publicacao e as
limitacoes conhecidas do ambiente. Para operacao local, veja o README.

## Topologia

| Componente | Servico | Observacao |
| --- | --- | --- |
| Aplicacao | Vercel (plano Hobby) | App inteiro roda como uma unica Function |
| Banco | Turso (libsql) | Obrigatorio: o filesystem da Vercel e efemero |

Nao ha frontend separado. O `bolao-profissa` e um monolito FastAPI que renderiza
Jinja2 e serve os proprios estaticos, entao a Vercel hospeda a aplicacao inteira.

## Como a Vercel monta o projeto

A Vercel usa o preset FastAPI e localiza sozinha a instancia `app` em `app/main.py`,
que e um dos entrypoints suportados. Disso decorrem tres pontos que evitam trabalho
desnecessario:

- nao e preciso criar `api/index.py`: um segundo entrypoint valido so gera ambiguidade
  sobre qual o build escolhe;
- nao e preciso declarar `rewrites`, porque todo o trafego ja vai para a Function;
- nao e preciso `requirements.txt`: as dependencias sao instaladas a partir de
  `[project.dependencies]` no `pyproject.toml`, que permanece a fonte unica de verdade.

O `vercel.json` existe apenas para elevar o `maxDuration` da Function. O padrao do
plano Hobby e curto demais para o primeiro request de uma instancia nova, que abre
conexao com a Turso e executa `init_db()`.

O mount `app.mount("/static", ...)` funciona normalmente; nao e necessario mover
ativos para `public/`.

## Variaveis de ambiente

Configuradas em Settings > Environment Variables. Nenhum valor pertence ao
repositorio: `.env` esta no `.gitignore` e assim deve permanecer.

| Variavel | Papel |
| --- | --- |
| `DATABASE_URL` | URL libsql da Turso, com `authToken` e `secure=true` na query |
| `SECRET_KEY` | Assinatura de sessao e CSRF |
| `ADMIN_TOKEN` | Autentica as rotas `/admin/seed` e `/admin/sync` |
| `ADMIN_PASSWORD` | Senha do usuario `admin` |
| `APP_ENV` | Deve ser `prod` |

Dois detalhes que costumam surpreender:

- `APP_ENV=prod` nao e cosmetico: define `https_only` no cookie de sessao
  (`app/main.py`). Sem ele o cookie vai sem a flag `Secure`.
- `_ensure_admin` (`app/db.py`) reescreve a senha do admin a cada boot com o valor
  da variavel. Alterar `ADMIN_PASSWORD` invalida a senha anterior no proximo deploy.

## Primeiro deploy

1. Criar o banco na Turso e gerar um token de escrita.
2. Importar o repositorio na Vercel mantendo o preset FastAPI e a raiz em `./`.
3. Cadastrar as cinco variaveis acima antes do primeiro build.
4. Publicar. O `init_db()` cria as tabelas e o usuario `admin` no primeiro request.
5. Popular times e partidas a partir de `data/seed/worldcup-2026.json`:

```bash
curl -X POST https://<app>.vercel.app/admin/seed -H "X-Admin-Token: <ADMIN_TOKEN>"
```

A resposta confirma o volume carregado (48 times, 69 jogos de grupo, 32 de mata-mata).
O seed roda com `force=False` e nao sobrescreve dados existentes.

## Verificacao pos-deploy

```bash
curl https://<app>.vercel.app/healthz          # {"ok":true}
curl -o /dev/null -w '%{http_code}\n' https://<app>.vercel.app/static/css/app.css
```

O `/healthz` so responde apos o lifespan concluir, e o lifespan executa `init_db()`.
Uma resposta valida portanto tambem confirma que a conexao com a Turso funciona.

## Limitacoes conhecidas

Registradas aqui por afetarem producao, mas nao resolvidas nesta entrega:

- **`init_db()` a cada cold start.** O lifespan executa `create_all`, as migracoes de
  compatibilidade e `_ensure_admin`, que calcula um hash bcrypt e grava no banco. Em
  serverless isso se repete a cada instancia nova, somando latencia e escritas
  desnecessarias. Convem condicionar a execucao a uma variavel de ambiente.
- **Rate limiting inefetivo.** O `slowapi` mantem contadores em memoria do processo.
  Com varias instancias, o limite efetivo se multiplica. Exigiria armazenamento
  compartilhado para valer de fato.
- **Sem migracoes versionadas.** `_run_compat_migrations` aplica `ALTER TABLE` com
  excecoes silenciadas. Funciona para o esquema atual, mas nao registra historico nem
  permite rollback.

## Rotacao de segredos

Tokens da Turso e `SECRET_KEY` podem ser trocados sem downtime: gere o novo valor,
atualize a variavel na Vercel e refaca o deploy. Revogue o valor antigo apenas depois
de confirmar que a nova versao esta no ar.
