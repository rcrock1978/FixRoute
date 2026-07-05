"""Azure Communication Services (ACS) SMS adapter."""
from __future__ import annotations

import logging
from typing import Any

from django.conf import settings

logger = logging.getLogger(__name__)


def send_sms(to_phone: str, body: str) -> dict[str, Any]:
    """Send an SMS via ACS. Returns the message receipt id."""
    if not settings.ACS_CONNECTION_STRING:
        logger.warning("acs.no_connection_string", extra={"to": to_phone})
        return {"receipt_id": None, "status": "noop"}
    from azure.communication.sms import SmsClient

    client = SmsClient.from_connection_string(settings.ACS_CONNECTION_STRING)
    response = client.send(
        from_=settings.ACS_SMS_FROM_NUMBER,
        to=[to_phone],
        message=body,
        enable_delivery_report=True,
    )
    receipt = response[0] if response else None
    logger.info(
        "sms.sent",
        extra={"to": to_phone, "receipt_id": getattr(receipt, "message_id", None)},
    )
    return {"receipt_id": getattr(receipt, "message_id", None), "status": "sent"}
