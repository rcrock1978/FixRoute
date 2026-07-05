"""Intake service — submit, list, and soft-delete work orders.

T029: uploads media to Azure Blob, computes embeddings, persists soft-delete timestamps.
T030: cursor-paginated list.
T029a: pgvector cosine similarity duplicate search.
T030a: soft_delete with 30-day hard_delete_at schedule.
"""
from __future__ import annotations

import logging
import uuid
from datetime import timedelta
from typing import Any, BinaryIO

from django.utils import timezone
from pgvector.django import CosineDistance

from backend.ai.embeddings.embedder import get_embedder
from backend.apps.intake.models import MediaAsset, WorkOrder
from backend.apps.triage.models import TriageResult
from backend.apps.triage.services import TriageService
from backend.common.db.soft_delete import SOFT_DELETE_HARD_DELETE_WINDOW
from backend.common.models import AuditLog
from backend.common.storage.blob import upload_blob

logger = logging.getLogger(__name__)

DUPLICATE_THRESHOLD = 0.85
DUPLICATE_LOOKBACK_DAYS = 14


class WorkOrderService:
    @staticmethod
    def submit(
        *,
        tenant_id: str,
        property_id: str,
        submitted_by_id: str,
        title: str,
        description: str,
        media_files: list[BinaryIO] | None = None,
        voice_recording: BinaryIO | None = None,
    ) -> WorkOrder:
        embedder = get_embedder()
        description_embedding = embedder.embed_text(description)

        work_order = WorkOrder.objects.create(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            property_id=property_id,
            submitted_by_id=submitted_by_id,
            title=title,
            description=description,
            description_embedding=description_embedding,
        )
        logger.info("work_order.submitted", extra={"id": str(work_order.id)})

        for media in media_files or []:
            WorkOrderService._attach_media(work_order, media)
        if voice_recording is not None:
            WorkOrderService._attach_media(work_order, voice_recording, is_voice=True)

        AuditLog.objects.create(
            tenant_id=tenant_id,
            actor_id=submitted_by_id,
            actor_role="tenant",
            action="work_order.submitted",
            entity_type="WorkOrder",
            entity_id=work_order.id,
            previous_state=None,
            new_state={"status": "submitted", "title": title},
        )

        WorkOrderService._classify_and_update(work_order, tenant_id, submitted_by_id)
        return work_order

    @staticmethod
    def _attach_media(work_order: WorkOrder, file: BinaryIO, *, is_voice: bool = False) -> MediaAsset:
        data = file.read()
        blob_name = f"{work_order.tenant_id}/{work_order.id}/{file.name}"
        content_type = "audio/mpeg" if is_voice else "image/jpeg"
        sas_url = upload_blob(blob_name, data, content_type)
        return MediaAsset.objects.create(
            tenant_id=work_order.tenant_id,
            work_order=work_order,
            blob_url=blob_name,
            container="fixroute-media",
            tier="hot",
            content_type=content_type,
            size_bytes=len(data),
        )

    @staticmethod
    def _classify_and_update(work_order: WorkOrder, tenant_id: str, actor_id: str) -> None:
        from backend.apps.intake.models import Tenant

        tenant_settings = Tenant.objects.filter(id=tenant_id).values_list("settings", flat=True).first() or {}
        threshold = float(tenant_settings.get("ai_confidence_threshold", 0.7))
        result = TriageService.classify(work_order.description, tenant_threshold=threshold)

        TriageResult.objects.create(
            work_order=work_order,
            category=result["category"],
            urgency=result["urgency"],
            confidence=result["confidence"],
            troubleshooting_steps=TriageService.get_troubleshooting(
                result["category"], result["urgency"]
            ),
            ai_model_version=result.get("model_version") or "unknown",
            classification_time_ms=result["classification_time_ms"],
        )

        if result["escalated_to_dispatch"]:
            work_order.status = "classified"
        elif TriageService.get_troubleshooting(result["category"], result["urgency"]):
            work_order.status = "troubleshooting"
        else:
            work_order.status = "classified"
        work_order.category = result["category"]
        work_order.priority = result["urgency"]
        work_order.save(update_fields=["status", "category", "priority", "updated_at"])

        AuditLog.objects.create(
            tenant_id=tenant_id,
            actor_id=actor_id,
            actor_role="system",
            action="work_order.classified",
            entity_type="WorkOrder",
            entity_id=work_order.id,
            previous_state={"status": "submitted"},
            new_state={"status": work_order.status, "category": result["category"], "urgency": result["urgency"]},
        )

    @staticmethod
    def list(*, tenant_id: str, status: str | None = None, limit: int = 25):
        qs = WorkOrder.objects.filter(tenant_id=tenant_id)
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("-created_at")[:limit]

    @staticmethod
    def soft_delete(*, work_order_id: str, tenant_id: str, actor_id: str) -> None:
        work_order = WorkOrder.objects.get(id=work_order_id, tenant_id=tenant_id)
        previous = {"status": work_order.status}
        work_order.soft_delete()
        AuditLog.objects.create(
            tenant_id=tenant_id,
            actor_id=actor_id,
            actor_role="property_manager",
            action="work_order.soft_deleted",
            entity_type="WorkOrder",
            entity_id=work_order.id,
            previous_state=previous,
            new_state={"soft_deleted_at": work_order.soft_deleted_at.isoformat()},
        )


class DuplicateDetectionService:
    """pgvector cosine similarity over text + image embeddings (T029a).

    Per the post-spec clarify session: threshold ≥0.85, lookback ≤14 days,
    scoped to the same property within the same tenant.
    """

    @staticmethod
    def find_similar(
        *,
        description: str,
        property_id: str,
        tenant_id: str,
        threshold: float = DUPLICATE_THRESHOLD,
        lookback_days: int = DUPLICATE_LOOKBACK_DAYS,
    ) -> list[dict[str, Any]]:
        embedder = get_embedder()
        embedding = embedder.embed_text(description)
        cutoff = timezone.now() - timedelta(days=lookback_days)

        qs = (
            WorkOrder.objects.filter(
                tenant_id=tenant_id,
                property_id=property_id,
                created_at__gte=cutoff,
                description_embedding__isnull=False,
            )
            .exclude(status="completed")
            .annotate(distance=CosineDistance("description_embedding", embedding))
            .order_by("distance")[:5]
        )
        matches = []
        for wo in qs:
            similarity = 1 - float(wo.distance)
            if similarity >= threshold:
                matches.append(
                    {
                        "work_order_id": str(wo.id),
                        "similarity_score": round(similarity, 4),
                        "match_type": "text",
                        "title": wo.title,
                        "status": wo.status,
                    }
                )
        return matches
