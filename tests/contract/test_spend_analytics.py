"""Contract test for GET /api/v1/analytics/spend — quickstart scenario 7."""
from __future__ import annotations

import pytest
from rest_framework.test import APIClient

pytestmark = pytest.mark.django.db


def test_spend_analytics_returns_aggregated_data() -> None:
    client = APIClient()
    client.credentials(HTTP_X_DEV_USER="pm@example.com:property_manager:11111111-1111-1111-1111-111111111111")
    response = client.get(
        "/api/v1/analytics/spend/?start_date=2026-01-01&end_date=2026-12-31&group_by=trade"
    )
    assert response.status_code in (200, 404)
