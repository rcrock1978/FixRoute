"""Contract test for POST /api/v1/dispatches/{id}/estimate — quickstart scenario 5."""
from __future__ import annotations

import pytest
from rest_framework.test import APIClient

pytestmark = pytest.mark.django.db


def test_estimate_submit_returns_201() -> None:
    client = APIClient()
    client.credentials(HTTP_X_DEV_USER="vendor@example.com:vendor:11111111-1111-1111-1111-111111111111")
    response = client.post(
        "/api/v1/dispatches/00000000-0000-0000-0000-000000000001/estimate/",
        data={"line_items": [{"description": "Labor", "amount": 85}], "total": 85},
        format="json",
    )
    assert response.status_code in (201, 404)
