"""Analytics service — spend aggregations by property, trade, vendor, time period per FR-010."""
from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal
from typing import Any

from django.db.models import Count, F, Sum
from django.db.models.functions import TruncDate, TruncMonth

logger = logging.getLogger(__name__)


class AnalyticsService:
    @staticmethod
    def get_spend(
        *,
        tenant_id: str,
        start_date: date,
        end_date: date,
        group_by: str = "trade",
    ) -> dict[str, Any]:
        from backend.apps.vendormanagement.models import CostEstimate

        if group_by not in ("property", "trade", "vendor", "month"):
            raise ValueError(f"invalid group_by: {group_by}")

        qs = CostEstimate.objects.filter(
            tenant_id=tenant_id,
            status="approved",
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
        )

        if group_by == "trade":
            from backend.apps.intake.models import WorkOrder
            from backend.apps.dispatch.models import Dispatch

            join_data = (
                qs.values("dispatch_id")
                .annotate(trade=WorkOrder.objects.filter(id=F("dispatch__work_order_id")).values("category")[:1])
                .values("trade")
                .annotate(total=Sum("total"), count=Count("id"))
                .order_by("-total")
            )
            return {
                "group_by": "trade",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "rows": [
                    {"trade": r["trade"], "total": float(r["total"] or 0), "count": r["count"]}
                    for r in join_data
                ],
            }
        if group_by == "vendor":
            from backend.apps.dispatch.models import Dispatch

            rows = (
                qs.annotate(vendor_id=F("dispatch__vendor_id"))
                .values("vendor_id")
                .annotate(total=Sum("total"), count=Count("id"))
                .order_by("-total")
            )
            return {
                "group_by": "vendor",
                "rows": [
                    {"vendor_id": str(r["vendor_id"]), "total": float(r["total"] or 0), "count": r["count"]}
                    for r in rows
                ],
            }
        if group_by == "month":
            rows = (
                qs.annotate(month=TruncMonth("created_at"))
                .values("month")
                .annotate(total=Sum("total"), count=Count("id"))
                .order_by("month")
            )
            return {
                "group_by": "month",
                "rows": [
                    {"month": r["month"].isoformat(), "total": float(r["total"] or 0), "count": r["count"]}
                    for r in rows
                ],
            }
        # property
        from backend.apps.intake.models import WorkOrder
        from backend.apps.dispatch.models import Dispatch

        rows = (
            qs.annotate(property_id=F("dispatch__work_order__property_id"))
            .values("property_id")
            .annotate(total=Sum("total"), count=Count("id"))
            .order_by("-total")
        )
        return {
            "group_by": "property",
            "rows": [
                {
                    "property_id": str(r["property_id"]),
                    "total": float(r["total"] or 0),
                    "count": r["count"],
                }
                for r in rows
            ],
        }
