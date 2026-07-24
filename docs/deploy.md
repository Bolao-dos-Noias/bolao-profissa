# Deploy em producao

Este documento descreve a topologia de produção, o procedimento de publicação e as
limitações conhecidas do ambiente. Para operação local, veja o README.

## Topologia

| Componente | Serviço | Observação |
| --- | --- | --- |
| Aplicação | Vercel (plano Hobby) | App inteiro roda como uma única Function |
| Banco | Turso (libsql) | Obrigatório: o filesystem da Vercel e efemero |

Não há frontend separado. O `bolao-profissa` e um monolito FastAPI que renderiza
Jinja2 e serve os próprios estáticos, então a Vercel hospeda a aplicação inteira.

## Como a Vercel monta o projeto

A Vercel usa o preset FastAPI e localiza sozinha a instância `app` em `app/main.py`,
que e um dos entrypoints suportados. Disso decorrem três pontos que evitam trabalho
desnecessário:

- não é preciso criar `api/index.py`: um segundo entrypoint válido só gera ambiguidade
  sobre qual o build escolhe;
- não é preciso declarar `rewrites`, porque todo o tráfego já vai para a Function;
- não é preciso `requirements.txt`: as dependências são instaladas a partir de
  `[project.dependencies]` no `pyproject.toml`, que permanece a fonte única de verdade.

O `vercel.json` existe apenas para elevar o `maxDuration` da Function. O padrão do
plano Hobby e curto demais para o primeiro request de uma instância nova, que abre
conexão com a Turso e executa `init_db()`.

O mount `app.mount("/static", ...)` funciona normalmente; não é necessário mover
ativos para `public/`.

## Variáveis de ambiente

Configuradas em Settings > Environment Variables. Nenhum valor pertence ao
repositório: `.env` está no `.gitignore` e assim deve permanecer.

| Variavel | Papel |
| --- | --- |
| `DATABASE_URL` | URL libsql da Turso, com `authToken` e `secure=true` na query |
| `SECRET_KEY` | Assinatura de sessão e CSRF |
| `ADMIN_TOKEN` | Autentica as rotas `/admin/seed` e `/admin/sync` |
| `ADMIN_PASSWORD` | Senha do usuário `admin` |
| `APP_ENV` | Deve ser `prod` |

Dois detalhes que costumam surpreender:

- `APP_ENV=prod` não é cosmético: define `https_only` no cookie de sessão
  (`app/main.py`). Sem ele o cookie vai sem a flag `Secure`.
- `_ensure_admin` (`app/db.py`) reescreve a senha do admin a cada boot com o valor
  da variavel. Alterar `ADMIN_PASSWORD` invalida a senha anterior no proximo deploy.

## Primeiro deploy

1. Criar o banco na Turso e gerar um token de escrita.
2. Importar o repositório na Vercel mantendo o preset FastAPI e a raiz em `./`.
3. Cadastrar as cinco variáveis acima antes do primeiro build.
4. Publicar. O `init_db()` cria as tabelas e o usuário `admin` no primeiro request.
5. Popular times e partidas a partir de `data/seed/worldcup-2026.json`:

```bash
curl -X POST https://<app>.vercel.app/admin/seed -H "X-Admin-Token: <ADMIN_TOKEN>"
```

A resposta confirma o volume carregado (48 times, 69 jogos de grupo, 32 de mata-mata).
O seed roda com `force=False` e não sobrescreve dados existentes.

## Verificação pós-deploy

```bash
curl https://<app>.vercel.app/healthz          # {"ok":true}
curl -o /dev/null -w '%{http_code}\n' https://<app>.vercel.app/static/css/app.css
```

O `/healthz` só responde após o lifespan concluir, e o lifespan executa `init_db()`.
Uma resposta válida portanto também confirma que a conexão com a Turso funciona.

## Limitações conhecidas

Registradas aqui por afetarem produção, mas não resolvidas nesta entrega:

- **`init_db()` a cada cold start.** O lifespan executa `create_all`, as migrações de
  compatibilidade e `_ensure_admin`, que calcula um hash bcrypt e grava no banco. Em
  serverless isso se repete a cada instância nova, somando latência e escritas
  desnecessárias. Convém condicionar a execução à uma variável de ambiente.
- **Rate limiting inefetivo.** O `slowapi` mantém contadores em memória do processo.
  Com várias instâncias, o limite efetivo se multiplica. Exigiria armazenamento
  compartilhado para valer de fato.
- **Sem migrações versionadas.** `_run_compat_migrations` aplica `ALTER TABLE` com
  exceções silenciadas. Funciona para o esquema atual, mas não registra histórico nem
  permite rollback.

## Rotação de segredos

Tokens da Turso e `SECRET_KEY` podem ser trocados sem downtime: gere o novo valor,
atualize a variável na Vercel e refaça o deploy. Revogue o valor antigo apenas depois
de confirmar que a nova versão esta no ar.
