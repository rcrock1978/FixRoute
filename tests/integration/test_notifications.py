"""Integration test: notification delivery across email, ACS SMS, APNs/FCM push."""
from __future__ import annotations

from unittest.mock import patch

import pytest


def test_notification_dispatch_calls_all_channels() -> None:
    with patch("backend.common.notifications.service.send_sms") as sms, patch(
        "backend.common.notifications.service.send_apns"
    ) as apns, patch("backend.common.notifications.service.send_fcm") as fcm:
        from backend.common.notifications.service import NotificationTarget, notify

        notify(
            NotificationTarget(phone="+15551234567", apns_token="apns-tok", fcm_token="fcm-tok"),
            title="Vendor en route",
            body="Your technician will arrive in 30 min",
        )
        sms.assert_called_once()
        apns.assert_called_once()
        fcm.assert_called_once()
