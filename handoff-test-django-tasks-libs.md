# Handoff — test_django_tasks_libs

**Data:** 2025-07  
**Projeto:** `/home/weverton/Documentos/github/test_django_tasks_libs`  
**Estado:** Design finalizado via entrevista /grill-me. Pronto para implementação. Nenhum código escrito ainda.

---

## Contexto

O objetivo é construir um pequeno app Django para comparar quatro bibliotecas de task queue que usam PostgreSQL como broker, com integração com o Django Admin:

- `django-huey`
- `django-tasks-db`
- `django-dramatiq` (com `dramatiq-pg` como broker Postgres)
- `django-q2`

---

## Decisões acordadas

Todas as decisões estão documentadas com detalhes em:

> `/home/weverton/Documentos/github/test_django_tasks_libs/GRILL-ME.md`

Resumo executivo:

| Decisão | Escolha |
|---|---|
| Package manager | `uv` |
| Django | 5.2 LTS |
| Python (Docker) | 3.12 |
| Infraestrutura | Docker Compose |
| Broker dramatiq | `django-dramatiq` + `dramatiq-pg` (Postgres puro, sem Redis) |
| Estrutura de apps | 1 app por lib + `core/` compartilhado |
| Task demo | `generate_report(n)` — sleep n seg, salva resultado no banco |
| Model compartilhado | `core.Report` com `source`, `status`, `duration_seconds`, `started_at`, `finished_at` |
| Admin | Models nativos de cada lib + admin action no `Report` para disparar task |
| Trigger manual | Admin action + `manage.py run_task <lib> <n>` |
| Superusuário | Criado via env vars no entrypoint do Docker Compose |
| Workers | Um serviço por lib no Compose: `worker_huey`, `worker_dramatiq`, `worker_q2`, `worker_tasks_db` |
| Settings | Um único `settings.py` |

---

## Estrutura de arquivos esperada

```
test_django_tasks_libs/
├── config/                  # settings.py, urls.py, wsgi.py, asgi.py
├── core/                    # Report model, management command run_task
│   ├── models.py            # Report(source, status, duration_seconds, started_at, finished_at)
│   ├── admin.py             # Report admin com list_filter por source
│   └── management/commands/run_task.py
├── app_huey/                # tasks.py, admin.py (models nativos do huey)
├── app_dramatiq/            # tasks.py, admin.py (models nativos do dramatiq)
├── app_q2/                  # tasks.py, admin.py (models nativos do q2)
├── app_tasks_db/            # tasks.py, admin.py (models nativos do tasks_db)
├── docker-compose.yml       # db, web, worker_huey, worker_dramatiq, worker_q2, worker_tasks_db
├── Dockerfile               # python:3.12, uv, entrypoint.sh
├── entrypoint.sh            # migrate + createsuperuser --no-input + runserver
├── pyproject.toml           # dependências gerenciadas por uv
└── GRILL-ME.md              # decisões completas
```

---

## Riscos em aberto

1. **`dramatiq-pg` 0.12.0 + `django-dramatiq` + Django 5.2** — compatibilidade não verificada na prática. Checar se `dramatiq-pg` expõe corretamente o `PgBroker` e se `django-dramatiq` aceita broker customizado.
2. **`django-tasks-db`** — API ainda nova; verificar se tem management command de worker ou usa `CONN_MAX_AGE`.
3. **`django-q2` + Django 5.2** — verificar compatibilidade antes de fixar versão no `pyproject.toml`.
4. **`django-huey`** — confirmar se usa `HUEY` dict config ou `HUEY` object direto no settings.

---

## Próximos passos para o agente

1. Verificar compatibilidade de versões de todas as libs com Django 5.2 + Python 3.12 **antes** de escrever código:
   ```bash
   uv pip index versions django-huey django-tasks-db django-dramatiq dramatiq-pg django-q2
   ```
2. Criar `pyproject.toml` com `uv init` e fixar dependências.
3. Gerar o projeto Django com `django-admin startproject config .`
4. Criar os 5 apps: `core`, `app_huey`, `app_dramatiq`, `app_q2`, `app_tasks_db`.
5. Implementar `core.Report` model e migration.
6. Implementar `generate_report(n)` em cada app.
7. Configurar admin de cada app (models nativos + action).
8. Escrever `management/commands/run_task.py`.
9. Escrever `Dockerfile`, `entrypoint.sh`, `docker-compose.yml`.
10. Testar `docker compose up` e verificar workers conectando ao Postgres.

---

## Ambiente local

- Python local: 3.14.6 (não usar — usar 3.12 via Docker)
- Django instalado globalmente: 6.0.3 (não usar — fixar 5.2 no projeto)
- Nenhuma das libs de tasks está instalada ainda
- Diretório do projeto vazio: `/home/weverton/Documentos/github/test_django_tasks_libs`

---

## Suggested skills

- **grilling** (`/home/weverton/.agents/skills/grilling/SKILL.md`) — se surgirem novas decisões de design durante a implementação (ex.: estrutura do admin, campos adicionais no Report), use o skill de grilling para resolver antes de codificar.

---

## Informações redatadas

- Credenciais do banco de dados: use valores placeholder como `postgres`/`postgres` no Compose para ambiente de desenvolvimento local. Não commitar credenciais reais.
