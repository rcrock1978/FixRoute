"""Celery tasks — erasure sweep, pgvector maintenance, tombstone reconciliation."""
from __future__ import annotations

import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name="backend.common.tasks.erasure.run_erasure_sweep")
def run_erasure_sweep() -> dict[str, int]:
    """Hard-delete records past their 30-day window. Write tombstones to AuditLog."""
    from backend.common.db.soft_delete import SoftDeleteModel
    from django.apps import apps

    hard_deleted = 0
    for model in apps.get_models():
        if not issubclass(model, SoftDeleteModel):
            continue
        for obj in model.all_objects.due_for_hard_delete():  # type: ignore[attr-defined]
            obj.hard_delete(
                tombstone_payload={
                    "tenant_id": str(getattr(obj, "tenant_id", "")),
                    "entity_id": str(obj.pk),
                    "erased_at": timezone.now().isoformat(),
                }
            )
            hard_deleted += 1
    logger.info("erasure.sweep.complete", extra={"hard_deleted": hard_deleted})
    return {"hard_deleted": hard_deleted}


@shared_task(name="backend.common.tasks.pgvector_maintenance.reindex_hnsw")
def reindex_hnsw() -> None:
    """Reindex pgvector HNSW indexes weekly to maintain recall."""
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute("REINDEX INDEX CONCURRENTLY workorder_description_embedding_idx")
    logger.info("pgvector.hnsw.reindexed")


@shared_task(name="backend.common.tasks.reconciliation.reconcile_tombstones")
def reconcile_tombstones() -> dict[str, int]:
    """Verify every ErasureRequest has a corresponding AuditLog tombstone within 30 days.

    Per SC-006: any missing tombstone indicates an SLA breach and triggers an alert.
    """
    from backend.common.models import AuditLog

    breach_count = 0
    cutoff = timezone.now() - timedelta(days=30)
    for log in AuditLog.objects.filter(action="entity.hard_deleted", is_tombstone=True):
        if log.timestamp < cutoff and not AuditLog.objects.filter(
            action="tombstone.reconciled", entity_id=log.entity_id
        ).exists():
            breach_count += 1
    if breach_count:
        logger.error("reconciliation.sla_breach", extra={"count": breach_count})
    return {"breaches": breach_count}
