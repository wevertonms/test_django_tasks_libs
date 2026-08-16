# Grill Me Results

Generated: 2026-08-16T14:26:08.569Z

## Plan

(state was created by grill_record_turn; no plan recorded)

## Shared Understanding

App Django para comparar 4 libs de tasks usando PostgreSQL como broker: django-huey, django-tasks-db, django-dramatiq (+ dramatiq-pg), django-q2. Um app por lib + core compartilhado. Task demo generate_report(n). Admin com models nativos + action. Workers isolados no Docker Compose.

## Questions and Answers

### 1. Gerenciador de dependências / ambiente virtual

**Recommended answer:** uv

**User answer:** uv

**Status:** resolved

### 2. Versão do Django

**Recommended answer:** Django 5.2 LTS

**User answer:** 5.2

**Status:** resolved

### 3. Infraestrutura do PostgreSQL

**Recommended answer:** Docker Compose

**User answer:** docker compose

**Status:** resolved

### 4. Estrutura do projeto Django

**Recommended answer:** Um app por lib, com app core/ compartilhado

**User answer:** um app por lib

**Status:** resolved

### 5. Tasks de demonstração

**Recommended answer:** A mesma task em todas as libs — simula algo real com sleep + salva resultado no banco

**User answer:** A mesma task em todas as libs

**Status:** resolved

### 6. O que a task de demonstração faz?

**Recommended answer:** generate_report(n) — dorme n segundos, grava Report model no banco com status, duração e timestamp

**User answer:** Siga com a recomendação

**Status:** resolved

### 7. Integração com Django Admin

**Recommended answer:** Models nativos registrados + admin action no Report model para disparar generate_report

**User answer:** Siga com a recomendação

**Status:** resolved

### 8. Settings: um arquivo ou múltiplos?

**Recommended answer:** Um único settings.py com todas as libs configuradas juntas

**User answer:** Siga com a recomendação

**Status:** resolved

### 9. Workers no Docker Compose

**Recommended answer:** Um serviço por worker: worker_huey, worker_dramatiq, worker_q2, worker_tasks_db + web + db

**User answer:** Siga com a recomendação

**Status:** resolved

### 10. django-dramatiq usa broker intermediário — como resolver?

**Recommended answer:** Usar django-dramatiq + dramatiq-pg como broker PostgreSQL, sem Redis

**User answer:** Confirmo dramatiq-pg

**Status:** resolved

### 11. Como disparar as tasks para teste?

**Recommended answer:** Admin action no Report model + management command run_task &lt;lib&gt; &lt;n&gt;

**User answer:** Siga com a recomendação

**Status:** resolved

### 12. Superusuário do Admin

**Recommended answer:** Variável de ambiente no Docker Compose, criado via createsuperuser --no-input no entrypoint

**User answer:** Siga com a recomendação

**Status:** resolved

### 13. Model Report: compartilhado ou por lib?

**Recommended answer:** App core/ compartilhado com único Report model, campos: source, status, duration_seconds, started_at, finished_at

**User answer:** Siga com a recomendação

**Status:** resolved

### 14. Versão do Python no Docker

**Recommended answer:** Python 3.12

**User answer:** 3.12

**Status:** resolved

## Agreed Decisions

- Package manager: uv
- Django 5.2 LTS
- Python 3.12 no Docker
- Infraestrutura: Docker Compose
- Broker dramatiq: django-dramatiq + dramatiq-pg (Postgres puro, sem Redis)
- Estrutura: 1 app por lib (app_huey, app_dramatiq, app_q2, app_tasks_db) + core/ compartilhado
- Task demo: generate_report(n) — sleep n segundos, salva resultado no banco
- Model: core.Report com campos source, status, duration_seconds, started_at, finished_at
- Admin: models nativos de cada lib registrados + admin action no Report para disparar task
- Trigger: admin action + management command run_task <lib> <n>
- Superusuário: criado via variáveis de ambiente no entrypoint do Docker Compose
- Workers: um serviço por lib no Docker Compose (worker_huey, worker_dramatiq, worker_q2, worker_tasks_db)
- Settings: um único settings.py

## Open Risks

- Compatibilidade de dramatiq-pg 0.12.0 com django-dramatiq e Django 5.2 ainda não verificada na prática
- django-tasks-db pode ter limitações de API ainda não mapeadas
- django-q2 e django-huey precisam de verificação de compatibilidade com Django 5.2

## Next Decision Needed

Nenhuma — entendimento completo, pronto para implementação
