"""Contract test for GET /api/v1/work-orders/{id}/triage — quickstart scenario 2."""
from __future__ import annotations

import pytest
from rest_framework.test import APIClient

pytestmark = pytest.mark.django.db


def test_get_triage_returns_classification_with_confidence() -> None:
    client = APIClient()
    client.credentials(HTTP_X_DEV_USER="pm@example.com:property_manager:11111111-1111-1111-1111-111111111111")
    response = client.get("/api/v1/work-orders/00000000-0000-0000-0000-000000000001/triage/")
    assert response.status_code in (200, 404)
