"""App config to register common models for migration tracking."""
from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.common"
    label = "common"
    verbose_name = "Common"
