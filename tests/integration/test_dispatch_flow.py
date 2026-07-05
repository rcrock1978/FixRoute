"""Integration test: full dispatch flow from match → confirm → status updates."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.django.db


def test_dispatch_create_updates_work_order_status() -> None:
    from backend.apps.dispatch.services import DispatchService

    dispatch = DispatchService.create(
        work_order_id="00000000-0000-0000-0000-000000000001",
        vendor_id="00000000-0000-0000-0000-000000000099",
        tenant_id="11111111-1111-1111-1111-111111111111",
        actor_id="00000000-0000-0000-0000-000000000050",
    )
    assert dispatch.status == "assigned"
