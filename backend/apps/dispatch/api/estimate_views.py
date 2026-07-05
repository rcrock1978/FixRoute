"""Estimate + Analytics views (US3)."""
from __future__ import annotations

import logging
from decimal import Decimal

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from backend.apps.vendormanagement.api.serializers import (
    CostEstimateCreateSerializer,
    CostEstimateReviewSerializer,
    CostEstimateSerializer,
)
from backend.apps.dispatch.services_estimate import EstimateService
from backend.apps.vendormanagement.models import CostEstimate
from backend.common.auth.permissions import IsTenantMember

logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([IsTenantMember])
def submit_estimate(request: Request, dispatch_id: str) -> Response:
    serializer = CostEstimateCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    estimate = EstimateService.submit(
        dispatch_id=dispatch_id,
        tenant_id=str(request.tenant_id),
        actor_id=str(request.user.user_id),
        line_items=serializer.validated_data["line_items"],
        total=serializer.validated_data["total"],
    )
    return Response(CostEstimateSerializer(estimate).data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsTenantMember])
def review_estimate(request: Request, estimate_id: str) -> Response:
    serializer = CostEstimateReviewSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    if getattr(request.user, "role", "") not in ("property_manager", "maintenance_coordinator"):
        return Response(
            {"detail": "Only property_manager or maintenance_coordinator can review estimates"},
            status=status.HTTP_403_FORBIDDEN,
        )
    try:
        estimate = EstimateService.review(
            estimate_id=estimate_id,
            tenant_id=str(request.tenant_id),
            actor_id=str(request.user.user_id),
            action=serializer.validated_data["action"],
            comment=serializer.validated_data.get("comment", ""),
        )
    except CostEstimate.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    return Response(CostEstimateSerializer(estimate).data)
