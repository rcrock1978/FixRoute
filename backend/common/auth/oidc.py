"""OIDC/OAuth2 authentication via Microsoft Entra ID (Azure AD) — FR-013.

Validates JWT bearer tokens against Entra ID JWKS, extracts tenant_id, role,
and user_id claims, and binds a `User`-like principal onto `request.user`.

For local development, a development backdoor accepts a header like
`X-Dev-User: <email>:<role>:<tenant_id>` when DEBUG=True.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

import jwt
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.http import HttpRequest

logger = logging.getLogger(__name__)

_JWKS_CACHE: dict[str, Any] = {}
_JWKS_CACHE_TTL = 3600
_JWKS_FETCHED_AT: float = 0.0


@dataclass
class EntraClaims:
    user_id: str
    email: str
    tenant_id: str
    role: str  # one of: tenant, property_manager, maintenance_coordinator, vendor

    @property
    def is_authenticated(self) -> bool:
        return True


def _fetch_jwks() -> dict[str, Any]:
    global _JWKS_FETCHED_AT
    now = time.time()
    if _JWKS_CACHE and now - _JWKS_FETCHED_AT < _JWKS_CACHE_TTL:
        return _JWKS_CACHE
    import json
    import urllib.request

    url = (
        f"https://login.microsoftonline.com/{settings.ENTRA_ID_TENANT_ID}/discovery/v2.0/keys"
    )
    with urllib.request.urlopen(url, timeout=5) as resp:  # noqa: S310 — fixed Azure URL
        _JWKS_CACHE = json.loads(resp.read())
        _JWKS_FETCHED_AT = now
        return _JWKS_CACHE


def _validate_jwt(token: str) -> dict[str, Any]:
    jwks = _fetch_jwks()
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")
    key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
    if key is None:
        raise jwt.InvalidTokenError("No matching JWKS key")
    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
    return jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        audience=settings.ENTRA_ID_AUDIENCE,
        issuer=f"https://login.microsoftonline.com/{settings.ENTRA_ID_TENANT_ID}/v2.0",
    )


class EntraIDAuthentication:
    """DRF authentication class that validates Entra ID JWT bearer tokens."""

    def authenticate(self, request: HttpRequest) -> tuple[EntraClaims, str] | None:
        if settings.DEBUG and not getattr(settings, "PROD_AUTH_REQUIRED", False):
            dev = self._dev_backdoor(request)
            if dev is not None:
                return dev, "dev"

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None
        token = auth_header[7:]
        try:
            claims = _validate_jwt(token)
        except jwt.InvalidTokenError as exc:
            logger.warning("entra_id.jwt_invalid", extra={"error": str(exc)})
            return None

        principal = EntraClaims(
            user_id=claims["oid"],
            email=claims.get("preferred_username", ""),
            tenant_id=claims.get("tid", ""),
            role=claims.get("roles", ["tenant"])[0],
        )
        return principal, token

    @staticmethod
    def _dev_backdoor(request: HttpRequest) -> EntraClaims | None:
        dev = request.headers.get("X-Dev-User")
        if not dev:
            return None
        try:
            email, role, tenant_id = dev.split(":", 2)
        except ValueError:
            return None
        return EntraClaims(
            user_id=f"dev-{email}",
            email=email,
            tenant_id=tenant_id,
            role=role,
        )

    def authenticate_header(self, request: HttpRequest) -> str:
        return 'Bearer realm="fixroute"'


class EntraIDBackend(BaseBackend):
    """Django auth backend — required for permission checks against django-guardian."""

    def authenticate(self, request, username=None, password=None, **kwargs):  # type: ignore[override]
        return None

    def get_user(self, user_id):  # type: ignore[override]
        return None
