"""Django settings base — shared across dev/test/prod via env-driven overrides."""
from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-insecure-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "false").lower() == "true"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "guardian",
    "backend.apps.intake.apps.IntakeConfig",
    "backend.apps.triage.apps.TriageConfig",
    "backend.apps.dispatch.apps.DispatchConfig",
    "backend.apps.vendormanagement.apps.VendorManagementConfig",
    "backend.apps.analytics.apps.AnalyticsConfig",
    "backend.common.apps.CommonConfig",
]

MIDDLEWARE = [
    "backend.common.middleware.correlation_id.CorrelationIdMiddleware",
    "backend.common.middleware.tenant.TenantMiddleware",
    "backend.common.middleware.audit.AuditLogMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.config.urls"
WSGI_APPLICATION = "backend.config.wsgi.application"
ASGI_APPLICATION = "backend.config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "fixroute"),
        "USER": os.environ.get("POSTGRES_USER", "fixroute"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "fixroute"),
        "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": 60,
        "OPTIONS": {
            "pool": {"min_size": 1, "max_size": 20},
        },
    }
}

REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", REDIS_URL)
CELERY_TASK_ALWAYS_EAGER = os.environ.get("CELERY_EAGER", "false").lower() == "true"
CELERY_BEAT_SCHEDULE = {
    "erasure-sweep-daily": {
        "task": "backend.apps.compliance.tasks.run_erasure_sweep",
        "schedule": 24 * 60 * 60,
    },
    "pgvector-hnsw-maintenance": {
        "task": "backend.common.tasks.pgvector_maintenance.reindex_hnsw",
        "schedule": 7 * 24 * 60 * 60,
    },
    "tombstone-reconciliation": {
        "task": "backend.common.tasks.reconciliation.reconcile_tombstones",
        "schedule": 6 * 60 * 60,
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "backend.common.auth.oidc.EntraIDBackend",
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "backend.common.auth.oidc.EntraIDAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "backend.common.auth.permissions.IsTenantMember",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.CursorPagination",
    "PAGE_SIZE": 25,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.UserRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {"user": "1000/hour"},
}

SPECTACULAR_SETTINGS = {
    "TITLE": "FixRoute API",
    "DESCRIPTION": "AI-powered maintenance triage API",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

AZURE_BLOB_ACCOUNT_URL = os.environ.get("AZURE_BLOB_ACCOUNT_URL", "")
AZURE_BLOB_CONTAINER = os.environ.get("AZURE_BLOB_CONTAINER", "fixroute-media")
AZURE_BLOB_SAS_TTL_SECONDS = int(os.environ.get("AZURE_BLOB_SAS_TTL_SECONDS", "3600"))

ACS_CONNECTION_STRING = os.environ.get("ACS_CONNECTION_STRING", "")
ACS_SMS_FROM_NUMBER = os.environ.get("ACS_SMS_FROM_NUMBER", "")

APNS_KEY_ID = os.environ.get("APNS_KEY_ID", "")
APNS_TEAM_ID = os.environ.get("APNS_TEAM_ID", "")
APNS_BUNDLE_ID = os.environ.get("APNS_BUNDLE_ID", "")
FCM_CREDENTIALS_PATH = os.environ.get("FCM_CREDENTIALS_PATH", "")

ENTRA_ID_TENANT_ID = os.environ.get("ENTRA_ID_TENANT_ID", "")
ENTRA_ID_CLIENT_ID = os.environ.get("ENTRA_ID_CLIENT_ID", "")
ENTRA_ID_AUDIENCE = os.environ.get("ENTRA_ID_AUDIENCE", "")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "structlog.stdlib.ProcessorFormatter",
            "processor": "structlog.processors.JSONRenderer",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "loggers": {
        "": {"handlers": ["console"], "level": "INFO", "propagate": True},
    },
}

STRUCTLOG = {
    "processors": [
        "backend.common.logging.context.merge_correlation_context",
        "structlog.contextvars.merge_contextvars",
        "structlog.processors.add_log_level",
        "structlog.processors.TimeStamper(fmt="iso"),
        "structlog.processors.StackInfoRenderer",
        "structlog.processors.format_exc_info",
        "structlog.processors.JSONRenderer(),
    ],
    "wrapper_class": "structlog.stdlib.BoundLogger",
    "logger_factory": "structlog.stdlib.LoggerFactory",
    "cache_logger_on_first_use": True,
}

USE_TZ = True
