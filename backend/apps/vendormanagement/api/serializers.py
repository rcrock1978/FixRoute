"""Vendor + Dispatch + CostEstimate serializers."""
from __future__ import annotations

from rest_framework import serializers

from backend.apps.dispatch.models import Dispatch
from backend.apps.vendormanagement.models import CostEstimate, Vendor


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = [
            "id",
            "name",
            "trades",
            "coverage_areas",
            "availability",
            "rating",
            "contact_email",
            "contact_phone",
            "insurance_verified",
            "response_time_minutes",
            "hourly_rate",
            "created_at",
        ]
        read_only_fields = ["id", "rating", "created_at"]


class VendorMatchSerializer(serializers.Serializer):
    vendor_id = serializers.UUIDField()
    name = serializers.CharField()
    trade = serializers.CharField()
    score = serializers.FloatField()
    distance_km = serializers.FloatField()
    eta_minutes = serializers.IntegerField()
    rating = serializers.FloatField()
    estimated_cost = serializers.FloatField()
    insurance_verified = serializers.BooleanField()
    breakdown = serializers.DictField()


class DispatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispatch
        fields = [
            "id",
            "work_order",
            "vendor",
            "status",
            "estimated_cost",
            "final_cost",
            "estimated_arrival_at",
            "actual_arrival_at",
            "completed_at",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "actual_arrival_at",
            "completed_at",
            "created_at",
            "updated_at",
        ]


class DispatchCreateSerializer(serializers.Serializer):
    vendor_id = serializers.UUIDField()
    approval_token = serializers.CharField()


class CostEstimateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostEstimate
        fields = [
            "id",
            "dispatch_id",
            "line_items",
            "total",
            "variance",
            "status",
            "approved_by_id",
            "approved_at",
            "review_comment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "variance",
            "approved_by_id",
            "approved_at",
            "created_at",
            "updated_at",
        ]


class CostEstimateCreateSerializer(serializers.Serializer):
    line_items = serializers.ListField(child=serializers.DictField(), allow_empty=False)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)


class CostEstimateReviewSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["approve", "reject", "request_revision"])
    comment = serializers.CharField(required=False, allow_blank=True, default="")
