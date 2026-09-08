"""
Django settings for config project.

Compares four task queue libraries that use PostgreSQL as broker:
django-huey, django-tasks-db, django-dramatiq (dramatiq-pg), django-q2.
"""

import os
from pathlib import Path
from urllib.parse import quote_plus

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-dev-only")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_tasks_db",
    "django_dramatiq",
    "django_q",
    "huey.contrib.djhuey",
    "huey.contrib.djhuey.stats",
    "huey_monitor",
    "bx_django_utils",
    "chancy.contrib.django",
    "procrastinate.contrib.django",
    "flexiq.contrib.django",
    "app_chancy",
    "app_procrastinate",
    "app_flexiq",
    "core",
    "app_huey",
    "app_dramatiq",
    "app_q2",
    "app_tasks_db",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

POSTGRES_DB = os.environ.get("POSTGRES_DB", "tasks")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5433")


def pg_dsn() -> str:
    return (
        f"postgresql://{quote_plus(POSTGRES_USER)}:{quote_plus(POSTGRES_PASSWORD)}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": POSTGRES_DB,
        "USER": POSTGRES_USER,
        "PASSWORD": POSTGRES_PASSWORD,
        "HOST": POSTGRES_HOST,
        "PORT": POSTGRES_PORT,
        "CONN_MAX_AGE": 60,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# huey.contrib.djhuey (native huey Django integration)
# Uses the same PostgreSQL broker/queue as django-huey so both wrappers share
# the huey_* tables. Required for huey.contrib.djhuey.stats (huey admin).
# ---------------------------------------------------------------------------
HUEY = {
    "name": "huey",
    "huey_class": "huey.PostgresHuey",
    "immediate": False,
    "connection": {"dsn": pg_dsn()},
    "consumer": {
        "workers": 2,
        "loglevel": "INFO",
        "periodic": True,
    },
}

# ---------------------------------------------------------------------------
# django-dramatiq + dramatiq-pg (PostgreSQL broker)
# ---------------------------------------------------------------------------
DRAMATIQ_BROKER = {
    "BROKER": "dramatiq_pg.PostgresBroker",
    "OPTIONS": {
        "url": pg_dsn(),
    },
    "MIDDLEWARE": [
        "dramatiq.middleware.AgeLimit",
        "dramatiq.middleware.TimeLimit",
        "dramatiq.middleware.Callbacks",
        "dramatiq.middleware.Retries",
        "django_dramatiq.middleware.DbConnectionsMiddleware",
        "django_dramatiq.middleware.AdminMiddleware",
    ],
}

# ---------------------------------------------------------------------------
# django-q2 (ORM broker -> PostgreSQL)
# ---------------------------------------------------------------------------
Q_CLUSTER = {
    "name": "DjangoORM",
    "workers": 2,
    "recycle": 500,
    "timeout": 300,
    "retry": 360,
    "compress": True,
    "save_limit": 250,
    "queue_limit": 500,
    "cpu_affinity": 1,
    "label": "Django Q2",
    "orm": "default",
}

# ---------------------------------------------------------------------------
# django-tasks (official) + django-tasks-db backend
# ---------------------------------------------------------------------------
TASKS = {
    "default": {
        "BACKEND": "django_tasks_db.DatabaseBackend",
    }
}

# ---------------------------------------------------------------------------
# flexiq (Rust-powered, Postgres backend) — formerly taskito
# ---------------------------------------------------------------------------
FLEXIQ_BACKEND = "postgres"
FLEXIQ_DB_URL = pg_dsn()
FLEXIQ_SCHEMA = "flexiq"
