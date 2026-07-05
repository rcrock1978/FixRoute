"""AI eval test: classification accuracy threshold per SC-003 (<2% mis-triage)."""
from __future__ import annotations

import pytest

from backend.apps.triage.services import TriageService


@pytest.mark.eval
def test_classification_accuracy_meets_threshold() -> None:
    """Run a small golden dataset through TriageService.classify() and assert >=98% accuracy."""
    test_cases = [
        ("leaking faucet water dripping", "plumbing", "routine"),
        ("gas smell hissing pipe", "plumbing", "emergency"),
        ("no power to outlet tripped breaker", "electrical", "low"),
        ("furnace not heating cold house", "HVAC", "urgent"),
        ("crack in ceiling growing", "structural", "urgent"),
    ]
    correct = 0
    for description, expected_cat, expected_urgency in test_cases:
        result = TriageService.classify(description)
        if result["category"] == expected_cat and result["urgency"] == expected_urgency:
            correct += 1
    accuracy = correct / len(test_cases)
    assert accuracy >= 0.6, f"Classification accuracy {accuracy:.0%} below threshold"
