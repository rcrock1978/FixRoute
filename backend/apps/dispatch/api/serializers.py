"""Dispatch API serializers."""
from __future__ import annotations

from rest_framework import serializers

from backend.apps.dispatch.models import Dispatch


class DispatchStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=["accepted", "en_route", "on_site", "completed", "cancelled"]
    )
    notes = serializers.CharField(required=False, allow_blank=True, default="")
