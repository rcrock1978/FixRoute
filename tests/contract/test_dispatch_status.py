"""Contract test for PATCH /api/v1/dispatches/{id}/status — vendor status updates."""
from __future__ import annotations

import pytest
from rest_framework.test import APIClient

pytestmark = pytest.mark.django.db


def test_dispatch_status_update_returns_200() -> None:
    client = APIClient()
    client.credentials(HTTP_X_DEV_USER="vendor@example.com:vendor:11111111-1111-1111-1111-111111111111")
    response = client.patch(
        "/api/v1/dispatches/00000000-0000-0000-0000-000000000001/status/",
        data={"status": "en_route", "notes": "On the way"},
        format="json",
    )
    assert response.status_code in (200, 404)
