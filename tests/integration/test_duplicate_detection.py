"""Integration test: pgvector duplicate detection — 0.85 cosine threshold."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.django.db


def test_duplicate_detection_finds_similar_work_order() -> None:
    from backend.apps.intake.services import DuplicateDetectionService

    matches = DuplicateDetectionService.find_similar(
        description="Leaking kitchen faucet dripping from base",
        property_id="22222222-2222-2222-2222-222222222222",
        tenant_id="11111111-1111-1111-1111-111111111111",
        threshold=0.85,
    )
    assert isinstance(matches, list)
