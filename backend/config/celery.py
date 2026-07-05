"""Celery application bootstrap."""
from __future__ import annotations

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.config.settings.base")

app = Celery("fixroute")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(["backend.common.tasks", "backend.apps"])

app.conf.beat_schedule = {
    "erasure-sweep-daily": {
        "task": "backend.common.tasks.erasure.run_erasure_sweep",
        "schedule": crontab(hour=2, minute=0),
    },
    "pgvector-hnsw-maintenance": {
        "task": "backend.common.tasks.pgvector_maintenance.reindex_hnsw",
        "schedule": crontab(day_of_week=0, hour=3, minute=0),
    },
    "tombstone-reconciliation": {
        "task": "backend.common.tasks.reconciliation.reconcile_tombstones",
        "schedule": crontab(hour="*/6"),
    },
}
