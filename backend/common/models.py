"""Common app — base for cross-cutting models (AuditLog)."""
from __future__ import annotations

import uuid

from django.db import models


class AuditLog(models.Model):
    """Append-only record of all state-changing actions. Tombstones preserved on erasure."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField(db_index=True)
    actor_id = models.UUIDField(null=True, blank=True)
    actor_role = models.CharField(
        max_length=64,
        choices=[
            ("tenant", "Tenant"),
            ("property_manager", "Property Manager"),
            ("maintenance_coordinator", "Maintenance Coordinator"),
            ("vendor", "Vendor"),
            ("system", "System"),
        ],
    )
    action = models.CharField(max_length=128, db_index=True)
    entity_type = models.CharField(max_length=64, db_index=True)
    entity_id = models.UUIDField(db_index=True)
    previous_state = models.JSONField(null=True, blank=True)
    new_state = models.JSONField(null=True, blank=True)
    is_tombstone = models.BooleanField(
        default=False,
        help_text="True if this record documents an erasure/sweep event for referential integrity",
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "audit_logs"
        indexes = [
            models.Index(fields=["tenant_id", "entity_type", "entity_id"], name="audit_entity_idx"),
            models.Index(fields=["timestamp"], name="audit_time_idx"),
        ]
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return f"{self.action} {self.entity_type}:{self.entity_id} @ {self.timestamp.isoformat()}"
