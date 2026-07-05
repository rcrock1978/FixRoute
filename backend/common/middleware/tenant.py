"""Tenant middleware — extracts tenant from authenticated user, sets Postgres session var for RLS."""
from __future__ import annotations

from collections.abc import Callable

from django.http import HttpRequest, HttpResponse
from django.db import connection


class TenantMiddleware:
    """Binds authenticated user → Tenant and configures the DB session for RLS.

    For MVP, the tenant_id is read from the authenticated user's tenant_id claim
    (Entra ID token) and set as a Postgres session variable. RLS policies on
    every tenant-scoped table reference `current_setting('app.tenant_id')`.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        tenant_id = self._resolve_tenant_id(request)
        request.tenant_id = tenant_id  # type: ignore[attr-defined]

        if tenant_id is not None and connection.vendor == "postgresql":
            with connection.cursor() as cursor:
                cursor.execute("SET LOCAL app.tenant_id = %s", [str(tenant_id)])

        return self.get_response(request)

    @staticmethod
    def _resolve_tenant_id(request: HttpRequest) -> str | None:
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            return None
        return getattr(user, "tenant_id", None) or request.headers.get("X-Tenant-ID")
