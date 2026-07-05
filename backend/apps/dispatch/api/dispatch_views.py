"""Dispatch management endpoints — PATCH /dispatches/{id}/status (vendor-facing)."""
from __future__ import annotations

import logging

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from backend.apps.dispatch.api.serializers import DispatchStatusUpdateSerializer
from backend.apps.dispatch.models import Dispatch
from backend.apps.dispatch.services import DispatchService
from backend.apps.vendormanagement.api.serializers import DispatchSerializer

logger = logging.getLogger(__name__)


class DispatchViewSet(ViewSet):
    required_role = "vendor"

    def retrieve(self, request: Request, pk: str | None = None) -> Response:
        try:
            dispatch = Dispatch.objects.get(id=pk)
        except Dispatch.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(DispatchSerializer(dispatch).data)

    def partial_update(self, request: Request, pk: str | None = None) -> Response:
        serializer = DispatchStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            dispatch = DispatchService.update_status(
                dispatch_id=str(pk),
                new_status=serializer.validated_data["status"],
                actor_id=str(request.user.user_id),
                notes=serializer.validated_data.get("notes", ""),
            )
        except Dispatch.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(DispatchSerializer(dispatch).data)
