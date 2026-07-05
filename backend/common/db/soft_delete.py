"""Soft-delete base manager + queryset — soft-delete, schedule hard_delete_at=now+30d.

Per FR-014: tenant-scoped entities are soft-deleted immediately on erasure request
and hard-deleted 30 days later. Tombstones are written to AuditLog.
"""
from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.db import models, transaction
from django.utils import timezone


SOFT_DELETE_HARD_DELETE_WINDOW = timedelta(days=30)


class SoftDeleteQuerySet(models.QuerySet["SoftDeleteModel"]):
    def alive(self) -> "SoftDeleteQuerySet":
        return self.filter(soft_deleted_at__isnull=True)

    def dead(self) -> "SoftDeleteQuerySet":
        return self.filter(soft_deleted_at__isnull=False)

    def due_for_hard_delete(self) -> "SoftDeleteQuerySet":
        return self.filter(soft_deleted_at__isnull=False, hard_delete_at__lte=timezone.now())


class SoftDeleteManager(models.Manager.from_queryset(SoftDeleteQuerySet)):  # type: ignore[misc]
    def get_queryset(self) -> SoftDeleteQuerySet:
        return super().get_queryset().filter(soft_deleted_at__isnull=True)


class SoftDeleteModel(models.Model):
    """Abstract base. Concrete models must call .soft_delete() to set timestamps."""

    soft_deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)
    hard_delete_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(self, *, reason: str | None = None) -> None:
        now = timezone.now()
        self.soft_deleted_at = now
        self.hard_delete_at = now + SOFT_DELETE_HARD_DELETE_WINDOW
        self.save(update_fields=["soft_deleted_at", "hard_delete_at"])

    @transaction.atomic
    def hard_delete(self, *, tombstone_payload: dict[str, Any] | None = None) -> None:
        from backend.common.models import AuditLog

        if not self.soft_deleted_at:
            raise ValueError("hard_delete requires prior soft_delete")

        if tombstone_payload is not None:
            AuditLog.objects.create(
                tenant_id=getattr(self, "tenant_id", None) or tombstone_payload.get("tenant_id"),
                actor_role="system",
                action="entity.hard_deleted",
                entity_type=self.__class__.__name__,
                entity_id=self.pk,
                previous_state=tombstone_payload,
                new_state=None,
                is_tombstone=True,
            )
        super().delete()
