"""Correlation ID middleware — propagates X-Correlation-ID for log/trace stitching."""
from __future__ import annotations

import uuid
from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

CORRELATION_ID_HEADER = "X-Correlation-ID"


class CorrelationIdMiddleware:
    """Attach a correlation ID to every request/response for log stitching."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        cid = request.headers.get(CORRELATION_ID_HEADER) or str(uuid.uuid4())
        request.correlation_id = cid  # type: ignore[attr-defined]
        response = self.get_response(request)
        response[CORRELATION_ID_HEADER] = cid
        return response
