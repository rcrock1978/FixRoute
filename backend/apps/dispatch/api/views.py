"""WorkOrder dispatch-related endpoints (match + dispatch)."""
from __future__ import annotations

import logging
import secrets

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from backend.apps.dispatch.services import DispatchService
from backend.apps.intake.api.views import WorkOrderViewSet
from backend.apps.intake.models import WorkOrder
from backend.apps.vendormanagement.api.serializers import (
    DispatchCreateSerializer,
    VendorMatchSerializer,
)
from backend.apps.vendormanagement.services import VendorService

logger = logging.getLogger(__name__)


class DispatchActionViewSet(WorkOrderViewSet):
    """Adds /match-vendors and /dispatch actions to the work-orders viewset."""

    @action(detail=True, methods=["get"], url_path="match-vendors")
    def match_vendors(self, request: Request, pk: str | None = None) -> Response:
        work_order = WorkOrder.objects.get(id=pk, tenant_id=request.tenant_id)
        ranked = VendorService.match(
            trade=work_order.category or "general",
            postal_code=request.query_params.get("postal_code", "00000"),
            tenant_id=str(request.tenant_id),
        )
        return Response({"matches": VendorMatchSerializer(ranked, many=True).data})

    @action(detail=True, methods=["post"], url_path="dispatch")
    def dispatch(self, request: Request, pk: str | None = None) -> Response:
        serializer = DispatchCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            dispatch = DispatchService.create(
                work_order_id=str(pk),
                vendor_id=str(data["vendor_id"]),
                tenant_id=str(request.tenant_id),
                actor_id=str(request.user.user_id),
                actor_role=getattr(request.user, "role", "property_manager"),
                approval_token=data["approval_token"],
            )
        except (PermissionError, ValueError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except (WorkOrder.DoesNotExist, Exception) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        from backend.apps.vendormanagement.api.serializers import DispatchSerializer

        return Response(DispatchSerializer(dispatch).data, status=status.HTTP_201_CREATED)
