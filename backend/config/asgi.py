"""ASGI entry point for uvicorn / async workers."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.config.settings.prod")
application = get_asgi_application()
