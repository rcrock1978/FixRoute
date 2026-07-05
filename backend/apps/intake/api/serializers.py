"""DRF serializers for intake endpoints."""
from __future__ import annotations

from rest_framework import serializers

from backend.apps.intake.models import MediaAsset, Property, TenantProfile, WorkOrder


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ["id", "name", "address", "unit_count", "metadata", "created_at"]
        read_only_fields = ["id", "created_at"]


class TenantProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantProfile
        fields = ["id", "property", "name", "email", "phone", "unit", "created_at"]
        read_only_fields = ["id", "created_at"]


class WorkOrderMediaField(serializers.JSONField):
    """Returns media as [{blob_url, sas_token_expires_at, tier, type, filename}, ...]."""

    def to_representation(self, value):
        from django.conf import settings
        from backend.common.storage.blob import generate_sas_url
        from datetime import datetime, timezone, timedelta

        items = []
        for asset in value.all():
            items.append(
                {
                    "blob_url": asset.blob_url,
                    "sas_token_expires_at": (
                        datetime.now(timezone.utc) + timedelta(seconds=settings.AZURE_BLOB_SAS_TTL_SECONDS)
                    ).isoformat(),
                    "container": asset.container,
                    "tier": asset.tier,
                    "type": asset.content_type,
                    "filename": asset.blob_url.rsplit("/", 1)[-1],
                }
            )
        return items


class WorkOrderSerializer(serializers.ModelSerializer):
    media_attachments = WorkOrderMediaField(source="media", read_only=True)

    class Meta:
        model = WorkOrder
        fields = [
            "id",
            "property",
            "submitted_by",
            "title",
            "description",
            "status",
            "priority",
            "category",
            "media_attachments",
            "voice_transcript",
            "soft_deleted_at",
            "hard_delete_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "priority",
            "category",
            "media_attachments",
            "soft_deleted_at",
            "hard_delete_at",
            "created_at",
            "updated_at",
        ]


class WorkOrderCreateSerializer(serializers.Serializer):
    property_id = serializers.UUIDField()
    title = serializers.CharField(max_length=200)
    description = serializers.CharField()
    media = serializers.ListField(
        child=serializers.FileField(), required=False, max_length=5
    )
    voice_recording = serializers.FileField(required=False, allow_null=True)


class TriageResultSerializer(serializers.Serializer):
    work_order_id = serializers.UUIDField()
    category = serializers.CharField()
    urgency = serializers.CharField()
    confidence = serializers.FloatField()
    troubleshooting_steps = serializers.ListField(child=serializers.DictField())
    ai_model_version = serializers.CharField()
    classification_time_ms = serializers.IntegerField()


class DuplicateMatchSerializer(serializers.Serializer):
    work_order_id = serializers.UUIDField()
    similarity_score = serializers.FloatField()
    match_type = serializers.CharField()
    title = serializers.CharField()
    status = serializers.CharField()
