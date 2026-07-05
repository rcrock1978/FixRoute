"""APNs/FCM push notification adapter — native client integration."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import jwt as pyjwt
from django.conf import settings

logger = logging.getLogger(__name__)


def _get_apns_token() -> str:
    """Mint a short-lived APNs provider auth token (JWT/ES256)."""
    key_path = Path(settings.APNS_KEY_PATH) if hasattr(settings, "APNS_KEY_PATH") else None
    if key_path is None or not key_path.exists():
        logger.warning("apns.no_key_path")
        return ""
    with open(key_path, "rb") as f:
        private_key = f.read()
    return pyjwt.encode(
        {"iss": settings.APNS_TEAM_ID, "iat": pyjwt.api_jws.datetime_now()},
        private_key,
        algorithm="ES256",
        headers={"kid": settings.APNS_KEY_ID, "alg": "ES256"},
    )


def send_apns(device_token: str, title: str, body: str, data: dict[str, Any] | None = None) -> None:
    """Send a push notification to an iOS device via APNs HTTP/2."""
    import httpx

    token = _get_apns_token()
    if not token:
        return
    url = f"https://api.push.apple.com/3/device/{device_token}"
    headers = {
        "authorization": f"bearer {token}",
        "apns-topic": settings.APNS_BUNDLE_ID,
        "apns-push-type": "alert",
    }
    payload = {
        "aps": {"alert": {"title": title, "body": body}, "sound": "default"},
        "data": data or {},
    }
    try:
        httpx.post(url, headers=headers, json=payload, timeout=5)
        logger.info("push.apns.sent", extra={"device": device_token[:8]})
    except httpx.HTTPError as exc:
        logger.error("push.apns.failed", extra={"error": str(exc)})


def send_fcm(device_token: str, title: str, body: str, data: dict[str, Any] | None = None) -> None:
    """Send a push notification to an Android device via Firebase Cloud Messaging."""
    import httpx
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request as GoogleRequest

    creds_path = settings.FCM_CREDENTIALS_PATH
    if not creds_path or not Path(creds_path).exists():
        logger.warning("fcm.no_credentials")
        return
    credentials = service_account.Credentials.from_service_account_file(
        creds_path, scopes=["https://www.googleapis.com/auth/firebase.messaging"]
    )
    credentials.refresh(GoogleRequest())
    url = "https://fcm.googleapis.com/v1/projects/{}/messages:send".format(
        json.loads(open(creds_path).read())["project_id"]
    )
    payload = {
        "message": {
            "token": device_token,
            "notification": {"title": title, "body": body},
            "data": {k: str(v) for k, v in (data or {}).items()},
        }
    }
    try:
        httpx.post(
            url,
            headers={"authorization": f"Bearer {credentials.token}"},
            json=payload,
            timeout=5,
        )
        logger.info("push.fcm.sent", extra={"device": device_token[:8]})
    except httpx.HTTPError as exc:
        logger.error("push.fcm.failed", extra={"error": str(exc)})
