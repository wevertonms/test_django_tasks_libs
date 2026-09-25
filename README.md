# test_django_tasks_libs

App Django para comparar **7 bibliotecas de task queue** que usam
**PostgreSQL como broker**, todas integradas ao Django Admin e rodando em
workers isolados via Docker Compose.

| Biblioteca | Stars | Última release | Último commit (main) | Broker | Worker |
| --- | --- | --- | --- | --- | --- |
| `huey` 3.4.0 (`huey.contrib.djhuey`) | ![Stars](https://img.shields.io/github/stars/coleifer/huey) | ![Release](https://img.shields.io/github/release-date/coleifer/huey) | ![Commit](https://img.shields.io/github/last-commit/coleifer/huey/master) | Postgres (`huey.PostgresHuey`) | `manage.py run_huey` |
| `django-dramatiq` 0.15.0 | ![Stars](https://img.shields.io/github/stars/Bogdanp/django_dramatiq) | ![Release](https://img.shields.io/github/release-date/Bogdanp/django_dramatiq) | ![Commit](https://img.shields.io/github/last-commit/Bogdanp/django_dramatiq/master) | Postgres (`dramatiq-pg`) | `manage.py rundramatiq` |
| `django-q2` 1.11.1 | ![Stars](https://img.shields.io/github/stars/django-q2/django-q2) | ![Release](https://img.shields.io/github/release-date/django-q2/django-q2) | ![Commit](https://img.shields.io/github/last-commit/django-q2/django-q2/master) | Postgres (ORM broker) | `manage.py qcluster` |
| `django-tasks-db` 0.13.0 | ![Stars](https://img.shields.io/github/stars/RealOrangeOne/django-tasks-db) | ![Release](https://img.shields.io/github/release-date/RealOrangeOne/django-tasks-db) | ![Commit](https://img.shields.io/github/last-commit/RealOrangeOne/django-tasks-db/master) | Postgres (`django_tasks_db`) | `manage.py db_worker` |
| `chancy` 0.25.1 | ![Stars](https://img.shields.io/github/stars/tktech/chancy) | ![Release](https://img.shields.io/github/release-date/tktech/chancy) | ![Commit](https://img.shields.io/github/last-commit/tktech/chancy/main) | Postgres (psycopg3) | `chancy worker start` |
| `procrastinate` 3.10.0 | ![Stars](https://img.shields.io/github/stars/procrastinate-org/procrastinate) | ![Release](https://img.shields.io/github/release-date/procrastinate-org/procrastinate) | ![Commit](https://img.shields.io/github/last-commit/procrastinate-org/procrastinate/main) | Postgres (psycopg) | `manage.py procrastinate worker` |
| `flexiq` 2.0.0 (Rust core, ex-taskito) | ![Stars](https://img.shields.io/github/stars/ByteVeda/flexiq) | ![Release](https://img.shields.io/github/release-date/ByteVeda/flexiq) | ![Commit](https://img.shields.io/github/last-commit/ByteVeda/flexiq/master) | Postgres (`flexiq[postgres]`) | `manage.py flexiq_worker` |

- Django 5.2 LTS · Python 3.12 · `uv` como gerenciador de pacotes.
- **Sem Redis**: as 7 filas vivem no mesmo PostgreSQL.

## Task de demonstração

Todas as libs executam a mesma task: `generate_report(n)` — dorme `n` segundos e
grava um registro em `core.Report` (`source`, `status`, `duration_seconds`,
`started_at`, `finished_at`). Serve como um comparativo drop-in de latência de
enqueue, execução e observabilidade.

## Estrutura

```text
config/                 # settings.py único com HUEY, DRAMATIQ_BROKER, Q_CLUSTER, TASKS, CHANCY e FLEXIQ
core/                   # Report model, admin e management command run_task
app_huey/               # tasks.py + admin action
app_dramatiq/           # tasks.py + admin action
app_q2/                 # tasks.py + admin action
app_tasks_db/           # tasks.py + admin action
app_chancy/             # tasks.py + admin action
app_procrastinate/      # tasks.py + admin action
app_flexiq/             # tasks.py + admin (flexiq contrib.django)
Dockerfile              # python:3.12-slim + uv
entrypoint.sh           # wait db + migrate + createsuperuser + schema dramatiq-pg + chancy migrate
docker-compose.yml      # db, web, worker_huey, worker_dramatiq, worker_q2, worker_tasks_db, worker_chancy, worker_procrastinate, worker_flexiq
```

## Como rodar

```bash
docker compose build
docker compose up -d
```

- Web/Admin: <http://localhost:8080/admin/>
- Login: `admin` / `admin` (configurável via `DJANGO_SUPERUSER_*` no Compose)
- Postgres do compose: `localhost:5433` (mapeado para o host), banco `tasks`,
usuário `postgres`/`postgres`

> Portas 8000 e 5432 já estavam ocupadas no ambiente de dev, então o compose usa
> `8080` e `5433`.

### Disparar tasks

Pelo terminal (no container web):

```bash
docker compose exec web .venv/bin/python manage.py run_task huey 5
docker compose exec web .venv/bin/python manage.py run_task dramatiq 5
docker compose exec web .venv/bin/python manage.py run_task q2 5
docker compose exec web .venv/bin/python manage.py run_task tasks_db 5
docker compose exec web .venv/bin/python manage.py run_task chancy 5
docker compose exec web .venv/bin/python manage.py run_task procrastinate 5
docker compose exec web .venv/bin/python manage.py run_task flexiq 5
```

Pelo Admin: em **Reports**, selecione um ou mais registros e use as ações
`Enqueue generate_report via Huey / Dramatiq / Django-Q2 / Django Tasks (DB) / Chancy / Procrastinate / FlexiQ`. A
duração usada é o `duration_seconds` do registro.

Cada worker roda em seu próprio container e consome apenas a própria fila.

## Configurações por biblioteca

Tudo está em `config/settings.py`:

- **huey** (integração nativa): `HUEY` (dict com `name`, `huey_class: huey.PostgresHuey` e `connection.dsn`), tabelas criadas automaticamente (`create_tables`). `huey.contrib.djhuey` + `huey.contrib.djhuey.stats` dão o worker (`run_huey`) e o monitoramento no admin. `django-huey-monitor` adiciona `TaskModel` + `SignalInfoModel` com tracking detalhado (progresso, sinais, parent task).
- **django-dramatiq**: `DRAMATIQ_BROKER` apontando para `dramatiq_pg.PostgresBroker` com `url`. O schema do broker é criado no `entrypoint.sh` via `generate_init_sql`.
- **django-q2**: `Q_CLUSTER` com `orm: "default"` (broker Postgres via ORM).
- **django-tasks-db**: `TASKS = {"default": {"BACKEND": "django_tasks_db.DatabaseBackend"}}` (backend oficial do framework `django-tasks`).
- **chancy**: `chancy.contrib.django` (tabelas criadas via `chancy misc migrate`). Usa `chancy_instance.chancy` para enqueue síncrono.
- **procrastinate**: `procrastinate.contrib.django` com `PROCRASTINATE_DATABASE_ALIAS = "default"`. Worker via `manage.py procrastinate worker`.
- **flexiq** (ex-taskito, renomeado na 1.0.0): `flexiq.contrib.django` (integração oficial). Backend Postgres via `FLEXIQ_BACKEND`, `FLEXIQ_DB_URL` e `FLEXIQ_SCHEMA` nas Django settings. Worker via `manage.py flexiq_worker` (o CLI standalone `flexiq worker --app` não chama `django.setup()`). Tabelas criadas automaticamente no schema `flexiq` na primeira conexão. Tasks rodam em contexto async — o body usa `@sync_to_async` para chamar o ORM.

## Admin

Além de `core.Report`, cada lib expõe seus models nativos de monitoramento:

| Lib | Models no Admin |
| --- | --- |
| huey | `HueyEvent` + `HueyDashboard` (`huey.contrib.djhuey.stats`); `TaskModel` + `SignalInfoModel` (`django-huey-monitor`) |
| django-dramatiq | `django_dramatiq.Task` (via AdminMiddleware) |
| django-q2 | `Schedule`, `Success`, `Failure`, `OrmQ` |
| django-tasks-db | `DBTaskResult` |
| chancy | `Job`, `Worker`, `Queue` (`chancy.contrib.django`) |
| procrastinate | `ProcrastinateJob` (`procrastinate.contrib.django`) |
| flexiq | Dashboard, Jobs, Dead Letters (`flexiq.contrib.django`) |

## Desenvolvimento local (fora do Docker)

```bash
uv sync                                  # cria .venv com Python 3.12
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5433                # porta do compose (ou a sua)
uv run python manage.py migrate
uv run python manage.py run_huey         # worker huey (um terminal por worker)
uv run python manage.py rundramatiq -p 1 -t 2
uv run python manage.py qcluster
uv run python manage.py db_worker --no-reload
uv run chancy --app chancy_instance.chancy worker start
uv run python manage.py procrastinate worker
uv run python manage.py flexiq_worker
uv run python manage.py run_task huey 2
```

## Notas e pegadinhas conhecidas

- **dramatiq-pg 0.12.0** declara `psycopg2` como dependência implícita — o projeto adiciona `psycopg2-binary` explicitamente.
- **django-tasks-db 0.13.0** deixou de declarar `django-tasks` como dependência (num Django 5.2 sem `django.tasks` embutido). O projeto adiciona `django-tasks` explicitamente; sem ele o import quebra em `django_tasks_db.compat` com `ValueError`.
- O CLI `dramatiq-pg` quebra no Python 3.12 (usa `distutils`, removido do stdlib); o `entrypoint.sh` inicializa o schema com `dramatiq_pg.schema.generate_init_sql` via psycopg2.
- huey conecta ao Postgres na importação (cria as tabelas da fila); o `entrypoint.sh` espera o banco ficar pronto antes de subir os containers.
- O worker `db_worker` do django-tasks-db herda `DEBUG` para ativar autoreload; no Compose é passado `--no-reload` para estabilidade.
- `django-huey-monitor` exige `bx_django_utils` no `INSTALLED_APPS` (warning `huey_monitor.E001` se ausente).
- **chancy** usa psycopg3 nativo (já presente nas deps). Suas tabelas são criadas pelo próprio `chancy misc migrate`, não pelo Django. Models são `managed=False`.
- **procrastinate** tem suporte Django oficial via `procrastinate[django]`. Worker roda como management command `manage.py procrastinate worker`.
- **flexiq** é um task queue com engine em Rust (Tokio + Diesel), renomeado de taskito na 1.0.0. Usa Postgres como backend compartilhado via `flexiq[postgres]`. Tabelas ficam em um schema dedicado (`flexiq`), criadas automaticamente na primeira conexão. O worker roda como management command `manage.py flexiq_worker`.
