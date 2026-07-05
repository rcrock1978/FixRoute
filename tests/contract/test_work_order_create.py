"""Contract tests for POST /api/v1/work-orders per quickstart scenario 1.

Tests are written first (red) per Constitution Principle III. The OpenAPI schema
in `specs/001-fixroute-platform/contracts/openapi.yaml` is the source of truth.
"""
from __future__ import annotations

import pytest
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


def test_submit_work_order_returns_201_with_created_status() -> None:
    client = APIClient()
    client.credentials(HTTP_X_DEV_USER="tenant@example.com:tenant:11111111-1111-1111-1111-111111111111")
    response = client.post(
        "/api/v1/work-orders/",
        data={
            "property_id": "22222222-2222-2222-2222-222222222222",
            "title": "Leaking kitchen faucet",
            "description": "Water is leaking from the base of the faucet",
        },
        format="json",
    )
    assert response.status_code == 201
    assert response.json()["status"] == "submitted"


def test_submit_work_order_invalid_property_returns_400() -> None:
    client = APIClient()
    client.credentials(HTTP_X_DEV_USER="tenant@example.com:tenant:11111111-1111-1111-1111-111111111111")
    response = client.post(
        "/api/v1/work-orders/",
        data={"title": "X", "description": "Y"},
        format="json",
    )
    assert response.status_code == 400
