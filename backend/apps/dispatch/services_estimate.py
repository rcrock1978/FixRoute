"""Estimate service — submit, review, and variance tracking per FR-008/FR-009.

T075: EstimateService.submit() — vendor creates estimate.
T076: EstimateService.review() — PM approves/rejects with comment.
T085v: EstimateService.record_completion() — persists variance on completion.
"""
from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from backend.common.models import AuditLog

logger = logging.getLogger(__name__)


class EstimateService:
    @staticmethod
    @transaction.atomic
    def submit(
        *,
        dispatch_id: str,
        tenant_id: str,
        actor_id: str,
        line_items: list[dict[str, Any]],
        total: Decimal,
    ) -> "CostEstimate":
        from backend.apps.vendormanagement.models import CostEstimate

        estimate = CostEstimate.objects.create(
            tenant_id=tenant_id,
            dispatch_id=dispatch_id,
            line_items=line_items,
            total=total,
            status="pending",
        )
        AuditLog.objects.create(
            tenant_id=tenant_id,
            actor_id=actor_id,
            actor_role="vendor",
            action="estimate.submitted",
            entity_type="CostEstimate",
            entity_id=estimate.id,
            previous_state=None,
            new_state={"status": "pending", "total": str(total)},
        )
        logger.info("estimate.submitted", extra={"id": str(estimate.id), "total": str(total)})
        return estimate

    @staticmethod
    @transaction.atomic
    def review(
        *,
        estimate_id: str,
        tenant_id: str,
        actor_id: str,
        action: str,
        comment: str = "",
    ) -> "CostEstimate":
        from backend.apps.vendormanagement.models import CostEstimate

        if action not in ("approve", "reject", "request_revision"):
            raise ValueError(f"invalid action: {action}")
        estimate = CostEstimate.objects.get(id=estimate_id, tenant_id=tenant_id)
        previous = estimate.status
        if action == "approve":
            estimate.status = "approved"
            estimate.approved_at = timezone.now()
        elif action == "reject":
            estimate.status = "rejected"
        else:
            estimate.status = "revised"
        estimate.approved_by_id = actor_id
        estimate.review_comment = comment
        estimate.save()

        AuditLog.objects.create(
            tenant_id=tenant_id,
            actor_id=actor_id,
            actor_role="property_manager",
            action=f"estimate.{action}d",
            entity_type="CostEstimate",
            entity_id=estimate.id,
            previous_state={"status": previous},
            new_state={"status": estimate.status, "comment": comment},
        )
        return estimate

    @staticmethod
    def compute_variance(*, estimated_total: Decimal, final_cost: Decimal) -> Decimal:
        """Compute variance = final_cost - estimated_total (positive = over budget)."""
        return final_cost - estimated_total

    @staticmethod
    def record_completion(
        *,
        estimate_id: str,
        final_cost: Decimal,
    ) -> "CostEstimate":
        from backend.apps.vendormanagement.models import CostEstimate

        estimate = CostEstimate.objects.get(id=estimate_id)
        estimate.variance = EstimateService.compute_variance(
            estimated_total=estimate.total, final_cost=final_cost
        )
        estimate.save(update_fields=["variance", "updated_at"])
        logger.info(
            "estimate.variance_recorded",
            extra={"id": str(estimate.id), "variance": str(estimate.variance)},
        )
        return estimate
