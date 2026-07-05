"""Triage bounded context — AI classification + troubleshooting knowledge base."""
from django.apps import AppConfig


class TriageConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.triage"
    label = "triage"
    verbose_name = "Triage"
