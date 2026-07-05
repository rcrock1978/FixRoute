"""Dispatch model — assignment of a Vendor to a WorkOrder."""
from __future__ import annotations

import uuid

from django.db import models

from backend.apps.intake.models import WorkOrder
from backend.apps.vendormanagement.models import Vendor


class Dispatch(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("assigned", "Assigned"),
        ("accepted", "Accepted"),
        ("en_route", "En Route"),
        ("on_site", "On Site"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work_order = models.ForeignKey(WorkOrder, on_delete=models.PROTECT, related_name="dispatches")
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name="dispatches")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="assigned", db_index=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    final_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_arrival_at = models.DateTimeField(null=True, blank=True)
    actual_arrival_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "dispatches"
        indexes = [
            models.Index(fields=["vendor", "status"], name="dispatch_vendor_status_idx"),
            models.Index(fields=["work_order"], name="dispatch_wo_idx"),
        ]
