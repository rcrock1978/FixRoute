"""Development settings — activates DEBUG and adds dev-only tooling."""
from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["*"]
CELERY_TASK_ALWAYS_EAGER = True
INTERNAL_IPS = ["127.0.0.1"]
