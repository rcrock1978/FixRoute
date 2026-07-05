"""Integration test: self-serve troubleshooting escalation per FR-003."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.django.db


def test_low_urgency_returns_troubleshooting_steps() -> None:
    from backend.apps.triage.services import TriageService

    result = TriageService.get_troubleshooting(category="plumbing", urgency="low")
    assert isinstance(result, list)
    assert len(result) >= 1
