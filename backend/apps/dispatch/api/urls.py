"""Dispatch URL routing — /dispatches/{id}/status."""
from __future__ import annotations

from django.urls import path

from backend.apps.dispatch.api.dispatch_views import DispatchViewSet

urlpatterns = [
    path("dispatches/<uuid:pk>/", DispatchViewSet.as_view({"get": "retrieve"})),
    path("dispatches/<uuid:pk>/status/", DispatchViewSet.as_view({"patch": "partial_update"})),
]
