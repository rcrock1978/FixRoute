"""Integration test: end-to-end intake-to-classification flow per FR-001/FR-002."""
from __future__ import annotations

import pytest
from rest_framework.test import APIClient

pytestmark = pytest.mark.django.db


def test_intake_classification_flow() -> None:
    client = APIClient()
    client.credentials(HTTP_X_DEV_USER="tenant@example.com:tenant:11111111-1111-1111-1111-111111111111")
    response = client.post(
        "/api/v1/work-orders/",
        data={
            "property_id": "22222222-2222-2222-2222-222222222222",
            "title": "Leaking kitchen faucet",
            "description": "Water leaking from base of faucet",
        },
        format="json",
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] in ("submitted", "classified", "troubleshooting")
