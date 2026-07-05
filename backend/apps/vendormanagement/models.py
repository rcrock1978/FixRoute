"""Vendor model — service provider with trade specialties and weighted matching criteria."""
from __future__ import annotations

import uuid

from django.db import models


class Vendor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=255)
    trades = models.JSONField(default=list, help_text="List of trade specialties: plumbing, electrical, HVAC, etc.")
    coverage_areas = models.JSONField(
        default=list, help_text="List of postal codes / geographic coverage areas"
    )
    availability = models.JSONField(default=dict, help_text="Schedule by day-of-week, hour ranges")
    rating = models.FloatField(default=0.0, help_text="Computed rating 0.0-5.0 (MVP: single field)")
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=32)
    insurance_verified = models.BooleanField(default=False)
    response_time_minutes = models.IntegerField(default=60)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    apns_token = models.CharField(max_length=255, blank=True, default="")
    fcm_token = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "vendors"
        indexes = [
            models.Index(fields=["tenant_id"], name="vendor_tenant_idx"),
        ]


class CostEstimate(models.Model):
    """Cost estimate from a vendor for a dispatch, with PM review workflow.

    T085w: `variance` field records final_cost - estimated_total at completion.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("revised", "Revised"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField(db_index=True)
    dispatch_id = models.UUIDField(db_index=True)
    line_items = models.JSONField(default=list, help_text="Array of {description, amount, type}")
    total = models.DecimalField(max_digits=10, decimal_places=2)
    variance = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="final_cost - total; set on dispatch.completed",
    )
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pending", db_index=True)
    approved_by_id = models.UUIDField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    review_comment = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cost_estimates"
        indexes = [
            models.Index(fields=["tenant_id", "status"], name="ce_tenant_status_idx"),
        ]
