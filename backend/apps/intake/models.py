"""Intake bounded context — Tenant, Property, TenantProfile, WorkOrder, MediaAsset."""
from __future__ import annotations

import uuid

from django.db import models
from pgvector.django import VectorField

from backend.common.db.soft_delete import SoftDeleteModel


class Tenant(SoftDeleteModel):
    """Root of multi-tenant isolation. Each property management company is one Tenant."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=64, unique=True)
    settings = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tenants"
        indexes = [
            models.Index(fields=["slug"], name="tenant_slug_idx"),
            models.Index(fields=["soft_deleted_at"], name="tenant_softdel_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.slug})"


class Property(models.Model):
    """A physical unit or building under management. Scoped to a Tenant."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=255)
    address = models.TextField()
    unit_count = models.IntegerField(default=1)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "properties"
        indexes = [models.Index(fields=["tenant_id"], name="property_tenant_idx")]


class TenantProfile(models.Model):
    """A resident living in a property. Distinct from Tenant (the property mgmt org)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField(db_index=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="residents")
    name = models.CharField(max_length=255)
    email = models.EmailField(db_index=True)
    phone = models.CharField(max_length=32, blank=True, default="")
    unit = models.CharField(max_length=32, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tenant_profiles"
        indexes = [
            models.Index(fields=["tenant_id", "email"], name="tenantprof_email_idx"),
        ]


class WorkOrder(SoftDeleteModel):
    """Central aggregate. Lifecycle: submitted → classified → troubleshooting → dispatched → in_progress → completed."""

    CATEGORY_CHOICES = [
        ("plumbing", "Plumbing"),
        ("electrical", "Electrical"),
        ("HVAC", "HVAC"),
        ("structural", "Structural"),
        ("appliance", "Appliance"),
        ("general", "General"),
    ]
    PRIORITY_CHOICES = [
        ("emergency", "Emergency"),
        ("urgent", "Urgent"),
        ("routine", "Routine"),
        ("low", "Low"),
    ]
    STATUS_CHOICES = [
        ("submitted", "Submitted"),
        ("classified", "Classified"),
        ("troubleshooting", "Troubleshooting"),
        ("dispatched", "Dispatched"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField(db_index=True)
    property = models.ForeignKey(Property, on_delete=models.PROTECT, related_name="work_orders")
    submitted_by = models.ForeignKey(
        TenantProfile, on_delete=models.PROTECT, related_name="submitted_work_orders"
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="submitted", db_index=True)
    priority = models.CharField(max_length=16, choices=PRIORITY_CHOICES, default="routine", db_index=True)
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES, null=True, blank=True)
    voice_transcript = models.TextField(blank=True, default="")
    description_embedding = VectorField(dimensions=1536, null=True, blank=True)
    image_embedding = VectorField(dimensions=512, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "work_orders"
        indexes = [
            models.Index(fields=["tenant_id", "status"], name="wo_tenant_status_idx"),
            models.Index(fields=["tenant_id", "-created_at"], name="wo_tenant_recent_idx"),
            models.Index(fields=["property", "status"], name="wo_property_status_idx"),
        ]


class MediaAsset(SoftDeleteModel):
    """Photo or voice recording stored in Azure Blob Storage, linked to a WorkOrder."""

    TIER_CHOICES = [("hot", "Hot"), ("cool", "Cool"), ("archive", "Archive")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField(db_index=True)
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name="media")
    blob_url = models.CharField(max_length=512)
    container = models.CharField(max_length=128)
    tier = models.CharField(max_length=16, choices=TIER_CHOICES, default="hot")
    content_type = models.CharField(max_length=64)
    size_bytes = models.BigIntegerField(null=True, blank=True)
    checksum_sha256 = models.CharField(max_length=64, blank=True, default="")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "media_assets"
        indexes = [
            models.Index(fields=["work_order"], name="media_wo_idx"),
            models.Index(fields=["soft_deleted_at"], name="media_softdel_idx"),
        ]

