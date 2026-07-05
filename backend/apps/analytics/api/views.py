"""Analytics views — /api/v1/analytics/spend/."""
from __future__ import annotations

from datetime import date

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from backend.apps.analytics.services import AnalyticsService
from backend.common.auth.permissions import IsTenantMember


@api_view(["GET"])
@permission_classes([IsTenantMember])
def spend_analytics(request: Request) -> Response:
    try:
        start = date.fromisoformat(request.query_params.get("start_date", ""))
        end = date.fromisoformat(request.query_params.get("end_date", ""))
    except ValueError:
        return Response({"detail": "start_date and end_date required (ISO 8601)"}, status=status.HTTP_400_BAD_REQUEST)
    group_by = request.query_params.get("group_by", "trade")
    try:
        data = AnalyticsService.get_spend(
            tenant_id=str(request.tenant_id),
            start_date=start,
            end_date=end,
            group_by=group_by,
        )
    except ValueError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(data)
