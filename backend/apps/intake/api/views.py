"""Intake API views — work order CRUD, triage, duplicate detection."""
from __future__ import annotations

import logging
import uuid

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from backend.apps.intake.api.serializers import (
    DuplicateMatchSerializer,
    TriageResultSerializer,
    WorkOrderCreateSerializer,
    WorkOrderSerializer,
)
from backend.apps.intake.models import WorkOrder
from backend.apps.intake.services import DuplicateDetectionService, WorkOrderService
from backend.apps.triage.models import TriageResult

logger = logging.getLogger(__name__)


class WorkOrderViewSet(ModelViewSet):
    serializer_class = WorkOrderSerializer
    required_role = "tenant"

    def get_queryset(self):
        return WorkOrder.objects.filter(tenant_id=self.request.tenant_id)

    def create(self, request: Request) -> Response:
        serializer = WorkOrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        work_order = WorkOrderService.submit(
            tenant_id=str(request.tenant_id),
            property_id=str(data["property_id"]),
            submitted_by_id=str(request.user.user_id),
            title=data["title"],
            description=data["description"],
            media_files=data.get("media"),
            voice_recording=data.get("voice_recording"),
        )
        return Response(WorkOrderSerializer(work_order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="triage")
    def triage(self, request: Request, pk: str | None = None) -> Response:
        try:
            result = TriageResult.objects.get(work_order_id=pk)
        except TriageResult.DoesNotExist:
            return Response({"detail": "Triage not yet complete."}, status=status.HTTP_404_NOT_FOUND)
        return Response(TriageResultSerializer(result).data)

    @action(detail=True, methods=["get"], url_path="duplicates")
    def duplicates(self, request: Request, pk: str | None = None) -> Response:
        work_order = WorkOrder.objects.get(id=pk, tenant_id=request.tenant_id)
        threshold = float(request.query_params.get("threshold", 0.85))
        matches = DuplicateDetectionService.find_similar(
            description=work_order.description,
            property_id=str(work_order.property_id),
            tenant_id=str(request.tenant_id),
            threshold=threshold,
        )
        return Response({"matches": DuplicateMatchSerializer(matches, many=True).data})

    @action(detail=True, methods=["post"], url_path="soft-delete")
    def soft_delete(self, request: Request, pk: str | None = None) -> Response:
        WorkOrderService.soft_delete(
            work_order_id=str(pk),
            tenant_id=str(request.tenant_id),
            actor_id=str(request.user.user_id),
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
