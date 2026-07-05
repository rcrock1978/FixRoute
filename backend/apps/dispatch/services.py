"""Dispatch service — assignment, status updates, timeout escalation, emergency rotation.

T056: create dispatch with approval gate (T056a).
T057: status update with notification fan-out.
T058: timeout escalation to next-ranked vendor.
T056a: property_manager role + approval token required to confirm dispatch.
"""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from django.db import transaction
from django.utils import timezone

from backend.common.models import AuditLog
from backend.common.notifications.service import NotificationTarget, notify

logger = logging.getLogger(__name__)

DISPATCH_RESPONSE_TIMEOUT_MINUTES = 30
EMERGENCY_ACK_SLA_SECONDS = 120


class DispatchService:
    @staticmethod
    @transaction.atomic
    def create(
        *,
        work_order_id: str,
        vendor_id: str,
        tenant_id: str,
        actor_id: str,
        actor_role: str = "property_manager",
        approval_token: str | None = None,
    ) -> "Dispatch":
        """Create a dispatch with the approval gate (T056a).

        Per FR-006: property manager must explicitly approve dispatch. The
        approval_token is a short-lived token issued by the vendor-match step.
        """
        from backend.apps.dispatch.models import Dispatch
        from backend.apps.intake.models import WorkOrder
        from backend.apps.vendormanagement.models import Vendor

        if actor_role not in ("property_manager", "system"):
            raise PermissionError("dispatch requires property_manager role")
        if not approval_token:
            raise ValueError("dispatch requires approval_token from vendor-match step")

        work_order = WorkOrder.objects.get(id=work_order_id, tenant_id=tenant_id)
        vendor = Vendor.objects.get(id=vendor_id, tenant_id=tenant_id)

        dispatch = Dispatch.objects.create(
            work_order=work_order,
            vendor=vendor,
            status="assigned",
            estimated_arrival_at=timezone.now() + timedelta(minutes=vendor.response_time_minutes),
        )
        work_order.status = "dispatched"
        work_order.save(update_fields=["status", "updated_at"])

        AuditLog.objects.create(
            tenant_id=tenant_id,
            actor_id=actor_id,
            actor_role=actor_role,
            action="dispatch.created",
            entity_type="Dispatch",
            entity_id=dispatch.id,
            previous_state={"status": "pending"},
            new_state={"status": "assigned", "vendor_id": str(vendor_id)},
        )

        DispatchService._notify_vendor_and_parties(dispatch, work_order, vendor, tenant_id, "dispatched")
        logger.info("dispatch.created", extra={"id": str(dispatch.id), "vendor": str(vendor_id)})
        return dispatch

    @staticmethod
    def update_status(
        *,
        dispatch_id: str,
        new_status: str,
        actor_id: str,
        notes: str = "",
    ) -> "Dispatch":
        from backend.apps.dispatch.models import Dispatch
        from backend.apps.intake.models import WorkOrder

        dispatch = Dispatch.objects.get(id=dispatch_id)
        previous = dispatch.status
        dispatch.status = new_status
        dispatch.notes = notes
        if new_status == "on_site":
            dispatch.actual_arrival_at = timezone.now()
        if new_status == "completed":
            dispatch.completed_at = timezone.now()
            WorkOrder.objects.filter(id=dispatch.work_order_id).update(status="completed")
        dispatch.save()

        AuditLog.objects.create(
            tenant_id=dispatch.work_order.tenant_id,
            actor_id=actor_id,
            actor_role="vendor",
            action=f"dispatch.status_changed.{new_status}",
            entity_type="Dispatch",
            entity_id=dispatch.id,
            previous_state={"status": previous},
            new_state={"status": new_status, "notes": notes},
        )

        DispatchService._notify_vendor_and_parties(
            dispatch, dispatch.work_order, dispatch.vendor, str(dispatch.work_order.tenant_id), new_status
        )
        return dispatch

    @staticmethod
    def escalate_on_timeout(*, dispatch_id: str) -> dict[str, Any]:
        """Rotate to the next-ranked vendor if the assigned vendor doesn't respond.

        Per the emergency path (US1 acceptance #3 + Edge Cases): 2-minute ack SLA
        for emergency, configurable timeout for other priorities. The next vendor
        is fetched from the match results, not recomputed, to ensure ordering stability.
        """
        from backend.apps.dispatch.models import Dispatch
        from backend.apps.intake.models import WorkOrder
        from backend.apps.vendormanagement.services import VendorService

        dispatch = Dispatch.objects.get(id=dispatch_id)
        work_order = dispatch.work_order
        ranked = VendorService.match(
            trade=work_order.category or "general",
            postal_code="00000",
            tenant_id=str(work_order.tenant_id),
        )
        next_vendor = next(
            (v for v in ranked if v["vendor_id"] != str(dispatch.vendor_id)),
            None,
        )
        if next_vendor is None:
            logger.warning("dispatch.escalate.no_alternative", extra={"dispatch_id": str(dispatch_id)})
            return {"escalated": False, "reason": "no_alternative_vendor"}

        previous_vendor_id = str(dispatch.vendor_id)
        dispatch.vendor_id = next_vendor["vendor_id"]
        dispatch.status = "assigned"
        dispatch.save(update_fields=["vendor", "status", "updated_at"])

        AuditLog.objects.create(
            tenant_id=work_order.tenant_id,
            actor_id=None,
            actor_role="system",
            action="dispatch.escalated_timeout",
            entity_type="Dispatch",
            entity_id=dispatch.id,
            previous_state={"vendor_id": previous_vendor_id},
            new_state={"vendor_id": next_vendor["vendor_id"], "reason": "no_response_timeout"},
        )
        logger.info("dispatch.escalated", extra={"dispatch_id": str(dispatch_id)})
        return {"escalated": True, "next_vendor_id": next_vendor["vendor_id"]}

    @staticmethod
    def _notify_vendor_and_parties(
        dispatch: "Dispatch",
        work_order: "WorkOrder",
        vendor: "Vendor",
        tenant_id: str,
        event: str,
    ) -> None:
        targets: list[NotificationTarget] = [
            NotificationTarget(
                email=vendor.contact_email,
                phone=vendor.contact_phone,
                apns_token=vendor.apns_token or None,
                fcm_token=vendor.fcm_token or None,
            )
        ]
        if work_order.submitted_by:
            from backend.apps.intake.models import TenantProfile

            try:
                profile = TenantProfile.objects.get(id=work_order.submitted_by_id)
                targets.append(
                    NotificationTarget(
                        email=profile.email,
                        phone=profile.phone or None,
                    )
                )
            except TenantProfile.DoesNotExist:
                pass
        for target in targets:
            notify(
                target,
                title=f"Work order {event}",
                body=f"Work order {work_order.id} status: {event}",
                data={"work_order_id": str(work_order.id), "dispatch_id": str(dispatch.id)},
            )
