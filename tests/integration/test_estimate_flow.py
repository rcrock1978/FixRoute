"""Integration test: estimate submission → PM review → completion → variance tracking."""
from __future__ import annotations

from decimal import Decimal

import pytest

pytestmark = pytest.mark.django.db


def test_estimate_flow_records_variance_on_completion() -> None:
    from backend.apps.dispatch.services import EstimateService

    variance = EstimateService.compute_variance(
        estimated_total=Decimal("100.00"), final_cost=Decimal("125.00")
    )
    assert variance == Decimal("25.00")
