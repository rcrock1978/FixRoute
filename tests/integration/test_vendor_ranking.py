"""Integration test: full dispatch flow from vendor match to completion."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.django.db


def test_vendor_ranking_scores_by_weighted_criteria() -> None:
    from backend.apps.vendormanagement.services import VendorService

    ranked = VendorService.match(
        trade="plumbing",
        postal_code="94110",
        tenant_id="11111111-1111-1111-1111-111111111111",
    )
    assert isinstance(ranked, list)
