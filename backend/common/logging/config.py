"""structlog config — JSON output with correlation ID + tenant context."""
from __future__ import annotations

import structlog

from backend.common.middleware.correlation_id import CORRELATION_ID_HEADER


def merge_correlation_context(_, __, event_dict):  # type: ignore[no-untyped-def]
    """structlog processor that pulls correlation_id from contextvars if present."""
    cid = structlog.contextvars.get_contextvars().get("correlation_id")
    if cid is not None:
        event_dict.setdefault("correlation_id", cid)
    return event_dict


def configure_logging() -> None:
    structlog.configure(
        processors=[
            merge_correlation_context,
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


__all__ = ["configure_logging", "merge_correlation_context", "CORRELATION_ID_HEADER"]
