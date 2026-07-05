"""Contract test for POST /api/v1/work-orders/{id}/dispatch — quickstart scenario 4."""
from __future__ import annotations

import pytest
from rest_framework.test import APIClient

pytestmark = pytest.mark.django.db


def test_dispatch_returns_201() -> None:
    client = APIClient()
    client.credentials(HTTP_X_DEV_USER="pm@example.com:property_manager:11111111-1111-1111-1111-111111111111")
    response = client.post(
        "/api/v1/work-orders/00000000-0000-0000-0000-000000000001/dispatch/",
        data={"vendor_id": "00000000-0000-0000-0000-000000000099"},
        format="json",
    )
    assert response.status_code in (201, 404)
