#!/usr/bin/env bash
set -euo pipefail

cd /app
source .venv/bin/activate

export DATABASE_URL="${DATABASE_URL:-postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres}@${POSTGRES_HOST:-db}:${POSTGRES_PORT:-5432}/${POSTGRES_DB:-tasks}}"

echo "Waiting for PostgreSQL..."
python - <<'PY'
import os
import time

import psycopg
from psycopg import OperationalError

dsn = os.environ["DATABASE_URL"]
for attempt in range(60):
    try:
        with psycopg.connect(dsn) as conn:
            conn.execute("SELECT 1")
        break
    except OperationalError as exc:
        print(f"  DB not ready (attempt {attempt + 1}): {exc}")
        time.sleep(2)
else:
    raise SystemExit("PostgreSQL is not available after 60 attempts.")
print("PostgreSQL is up.")
PY

n=0
until python manage.py migrate --noinput; do
  n=$((n + 1))
  if [ "$n" -ge 10 ]; then
    echo "migrate failed after $n attempts."
    exit 1
  fi
  echo "migrate failed (attempt $n), retrying..."
  sleep 2
done

if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ]; then
  python manage.py createsuperuser --noinput 2>/dev/null || \
    echo "Superuser ${DJANGO_SUPERUSER_USERNAME} already exists."
fi

echo "Running Chancy migrations..."
n=0
until PYTHONPATH=/app DJANGO_SETTINGS_MODULE=config.settings chancy --app chancy_instance.chancy misc migrate; do
  n=$((n + 1))
  if [ "$n" -ge 10 ]; then
    echo "chancy migrate failed after $n attempts."
    exit 1
  fi
  echo "chancy migrate failed (attempt $n), retrying..."
  sleep 2
done

python - <<'PY'
import os

import psycopg2
from psycopg2.errors import DuplicateObject, DuplicateTable

from dramatiq_pg.schema import generate_init_sql

dsn = os.environ["DATABASE_URL"]
conn = psycopg2.connect(dsn)
conn.autocommit = True
try:
    with conn.cursor() as curs:
        curs.execute(generate_init_sql())
except (DuplicateObject, DuplicateTable):
    pass
finally:
    conn.close()
PY

exec "$@"
