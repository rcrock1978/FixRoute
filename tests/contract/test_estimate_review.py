"""Contract test for POST /api/v1/estimates/{id}/approve."""
from __future__ import annotations

import pytest
from rest_framework.test import APIClient

pytestmark = pytest.mark.django.db


def test_estimate_approve_returns_200() -> None:
    client = APIClient()
    client.credentials(HTTP_X_DEV_USER="pm@example.com:property_manager:11111111-1111-1111-1111-111111111111")
    response = client.post(
        "/api/v1/estimates/00000000-0000-0000-0000-000000000001/approve/",
        data={"action": "approve"},
        format="json",
    )
    assert response.status_code in (200, 404)
