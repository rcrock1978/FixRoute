"""Intake bounded context — work order submission, media, duplicate detection."""
from django.apps import AppConfig


class IntakeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.intake"
    label = "intake"
    verbose_name = "Intake"
