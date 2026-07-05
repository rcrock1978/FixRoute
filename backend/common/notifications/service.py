"""Notification service — composes email + ACS SMS + APNs/FCM push per FR-007."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from backend.common.notifications.acs import send_sms
from backend.common.notifications.push import send_apns, send_fcm

logger = logging.getLogger(__name__)


@dataclass
class NotificationTarget:
    email: str | None = None
    phone: str | None = None
    apns_token: str | None = None
    fcm_token: str | None = None


def notify(
    target: NotificationTarget,
    *,
    title: str,
    body: str,
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Dispatch across all configured channels. Returns per-channel receipt ids."""
    receipts: dict[str, Any] = {}
    if target.phone:
        receipts["sms"] = send_sms(target.phone, body)
    if target.apns_token:
        send_apns(target.apns_token, title, body, data)
        receipts["apns"] = "sent"
    if target.fcm_token:
        send_fcm(target.fcm_token, title, body, data)
        receipts["fcm"] = "sent"
    if target.email:
        from django.core.mail import send_mail

        send_mail(title, body, "noreply@fixroute.example.com", [target.email])
        receipts["email"] = "sent"
    logger.info("notification.dispatched", extra={"receipts": receipts})
    return receipts
