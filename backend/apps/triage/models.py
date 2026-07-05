"""TriageResult — AI classification outcome linked 1:1 to a WorkOrder."""
from __future__ import annotations

import uuid

from django.db import models

from backend.apps.intake.models import WorkOrder


class TriageResult(models.Model):
    CATEGORY_CHOICES = WorkOrder.CATEGORY_CHOICES
    URGENCY_CHOICES = WorkOrder.PRIORITY_CHOICES

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work_order = models.OneToOneField(
        WorkOrder, on_delete=models.CASCADE, related_name="triage_result"
    )
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES)
    urgency = models.CharField(max_length=16, choices=URGENCY_CHOICES)
    confidence = models.FloatField()
    troubleshooting_steps = models.JSONField(default=list, blank=True)
    ai_model_version = models.CharField(max_length=64)
    classification_time_ms = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "triage_results"
