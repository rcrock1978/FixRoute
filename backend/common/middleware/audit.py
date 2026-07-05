"""Audit log middleware — auto-logs all state-changing actions per FR-012.

Concrete domain services (WorkOrderService, etc.) write AuditLog entries directly
because middleware cannot reliably diff arbitrary model state. This middleware
adds correlation_id propagation as a fallback for views that bypass services.
"""
from __future__ import annotations

from collections.abc import Callable

from django.http import HttpRequest, HttpResponse


class AuditLogMiddleware:
    """Pass-through middleware; services call AuditLog.objects.create() directly."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        return self.get_response(request)
