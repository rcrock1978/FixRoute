"""Triage service — orchestrates classification + troubleshooting + threshold gate.

Per FR-004 (per-tenant confidence threshold) and T035a: when AI confidence falls
below the tenant's threshold, escalate to human dispatch. Otherwise return
classification + troubleshooting steps.
"""
from __future__ import annotations

import logging
import time
from typing import Any

from backend.ai.classification.classifier import get_classifier
from backend.ai.troubleshooting.knowledge_base import lookup

logger = logging.getLogger(__name__)

DEFAULT_CONFIDENCE_THRESHOLD = 0.7


class TriageService:
    @staticmethod
    def classify(description: str, tenant_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD) -> dict[str, Any]:
        classifier = get_classifier()
        start = time.perf_counter()
        result = classifier.classify(description)
        elapsed_ms = int((time.perf_counter() - start) * 1000)

        confidence = float(result.get("confidence", 0.0))
        category = str(result.get("category", "general"))
        urgency = str(result.get("urgency", "routine"))

        escalated = confidence < tenant_threshold
        logger.info(
            "triage.classified",
            extra={
                "category": category,
                "urgency": urgency,
                "confidence": confidence,
                "threshold": tenant_threshold,
                "escalated": escalated,
                "latency_ms": elapsed_ms,
            },
        )

        return {
            "category": category,
            "urgency": urgency,
            "confidence": confidence,
            "model_version": result.get("model_version"),
            "escalated_to_dispatch": escalated,
            "classification_time_ms": elapsed_ms,
        }

    @staticmethod
    def get_troubleshooting(category: str, urgency: str) -> list[dict[str, Any]]:
        return lookup(category, urgency)
