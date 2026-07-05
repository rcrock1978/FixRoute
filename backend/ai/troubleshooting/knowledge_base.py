"""Troubleshooting knowledge base — returns step-by-step guidance for known patterns."""
from __future__ import annotations

from typing import Any

KNOWLEDGE_BASE: dict[str, list[dict[str, str]]] = {
    ("plumbing", "low"): [
        {"step": 1, "description": "Locate the shut-off valve under the sink and turn clockwise to close."},
        {"step": 2, "description": "Place a towel under the leak to absorb water."},
        {"step": 3, "description": "Tighten the P-trap connections by hand (1/4 turn with wrench)."},
        {"step": 4, "description": "Slowly reopen the valve. If leak persists, request vendor dispatch."},
    ],
    ("electrical", "low"): [
        {"step": 1, "description": "Check the circuit breaker panel for a tripped breaker."},
        {"step": 2, "description": "Flip the breaker fully OFF, then back to ON."},
        {"step": 3, "description": "Test the outlet. If still no power, request vendor dispatch."},
    ],
    ("HVAC", "low"): [
        {"step": 1, "description": "Replace the air filter (typically located in the return vent)."},
        {"step": 2, "description": "Verify the thermostat is set to COOL/HEAT and the target temperature."},
        {"step": 3, "description": "If problem persists after 30 minutes, request vendor dispatch."},
    ],
    ("appliance", "low"): [
        {"step": 1, "description": "Unplug the appliance for 60 seconds and plug back in (power cycle)."},
        {"step": 2, "description": "Check that water supply valves are fully open (if applicable)."},
        {"step": 3, "description": "If problem persists, request vendor dispatch."},
    ],
}


def lookup(category: str, urgency: str) -> list[dict[str, Any]]:
    """Return troubleshooting steps for a known (category, urgency) pattern.

    Returns an empty list if no pattern matches — caller falls through to dispatch.
    """
    return KNOWLEDGE_BASE.get((category, urgency), [])
