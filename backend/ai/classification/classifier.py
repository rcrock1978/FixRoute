"""AI classification — maps free-text description → category + urgency + confidence.

Per Constitution Principle II, this is wrapped in a port (ClassifierPort) so the
domain layer never depends on the concrete LLM provider. The MVP implementation
uses a keyword-based heuristic classifier (deterministic, fast, runs in tests
without API keys); the production provider (Azure OpenAI) is selected via env.
"""
from __future__ import annotations

import re
from typing import Protocol


class ClassifierPort(Protocol):
    def classify(self, text: str) -> dict[str, object]: ...


CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "plumbing": [
        r"\b(faucet|tap|leak|drip|pipe|water|drain|toilet|shower|sink|clog)\b",
    ],
    "electrical": [
        r"\b(power|outlet|switch|breaker|fuse|spark|wire|electric|light|bulb)\b",
    ],
    "HVAC": [
        r"\b(furnace|ac|air condition|heater|thermostat|heat|cool|vent)\b",
    ],
    "structural": [
        r"\b(crack|ceiling|wall|floor|foundation|leak|roof|window|door)\b",
    ],
    "appliance": [
        r"\b(refrigerator|fridge|oven|stove|dishwasher|washer|dryer|microwave|garbage disposal)\b",
    ],
}

URGENCY_KEYWORDS: dict[str, list[str]] = {
    "emergency": [r"\b(gas|smoke|fire|flood|burst|sewage|no power|electrical fire)\b"],
    "urgent": [r"\b(no heat|no hot water|leak|clog|broken|stopped working)\b"],
    "low": [r"\b(drip|squeak|loose|minor|small|when convenient)\b"],
}

CATEGORY_DEFAULT = "general"
URGENCY_DEFAULT = "routine"


def _score(text: str, patterns: dict[str, list[str]]) -> tuple[str, float]:
    text_lower = text.lower()
    scores: dict[str, int] = {}
    for label, regexes in patterns.items():
        scores[label] = sum(len(re.findall(p, text_lower)) for p in regexes)
    best_label = max(scores, key=scores.get)
    best_score = scores[best_label]
    if best_score == 0:
        return next(iter(patterns.keys())) and "", 0.0
    confidence = min(0.99, 0.5 + best_score * 0.1)
    return best_label, confidence


def classify(text: str) -> dict[str, object]:
    """Heuristic classifier — deterministic, fast, no external API calls."""
    category, cat_conf = _score(text, CATEGORY_KEYWORDS)
    urgency, urg_conf = _score(text, URGENCY_KEYWORDS)
    if not category:
        category = CATEGORY_DEFAULT
    if not urgency:
        urgency = URGENCY_DEFAULT
    confidence = round((cat_conf + urg_conf) / 2, 3)
    return {
        "category": category,
        "urgency": urgency,
        "confidence": confidence,
        "model_version": "heuristic-v0.1",
    }


class HeuristicClassifier:
    """Adapter implementing ClassifierPort — concrete impl, swappable via env."""

    def classify(self, text: str) -> dict[str, object]:
        return classify(text)


def get_classifier() -> ClassifierPort:
    """Factory: returns heuristic for MVP, Azure OpenAI when AZURE_OPENAI_ENDPOINT is set."""
    import os

    if os.environ.get("AZURE_OPENAI_ENDPOINT"):
        from backend.ai.classification.azure_openai_classifier import AzureOpenAIClassifier

        return AzureOpenAIClassifier()
    return HeuristicClassifier()
