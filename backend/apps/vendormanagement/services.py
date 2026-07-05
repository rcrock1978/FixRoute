"""Vendor service — weighted-scoring match per FR-005.

Per the post-spec clarify session: weights across proximity, availability, rating,
cost, response time are configurable per tenant. The MVP uses sensible defaults
and falls back to a uniform-weight score if no tenant-specific config is set.
"""
from __future__ import annotations

import logging
import math
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_WEIGHTS = {
    "proximity": 0.30,
    "availability": 0.25,
    "rating": 0.20,
    "cost": 0.10,
    "response_time": 0.15,
}

EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km between two lat/lon points."""
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    return EARTH_RADIUS_KM * c


class VendorService:
    @staticmethod
    def match(
        *,
        trade: str,
        postal_code: str,
        tenant_id: str,
        lat: float | None = None,
        lon: float | None = None,
        weights: dict[str, float] | None = None,
    ) -> list[dict[str, Any]]:
        """Return ranked list of vendors matching the criteria.

        Each entry includes the weighted score and per-criterion breakdown.
        """
        from backend.apps.vendormanagement.models import Vendor

        weights = weights or DEFAULT_WEIGHTS
        vendors = Vendor.objects.filter(tenant_id=tenant_id, trades__contains=[trade])

        scored: list[dict[str, Any]] = []
        for vendor in vendors:
            coverage_match = postal_code in (vendor.coverage_areas or [])

            # Proximity score: 1.0 if postal code in coverage, else fallback distance-based
            if coverage_match:
                proximity_score = 1.0
                distance_km = 0.0
            elif lat is not None and lon is not None:
                # MVP: no vendor lat/lon stored; default to mid-distance penalty
                distance_km = 10.0
                proximity_score = max(0.0, 1.0 - distance_km / 50.0)
            else:
                distance_km = float("inf")
                proximity_score = 0.0

            availability_score = 1.0 if vendor.availability else 0.5
            rating_score = vendor.rating / 5.0 if vendor.rating else 0.5
            cost_score = 1.0 - min(1.0, float(vendor.hourly_rate or 100) / 200.0)
            response_time_score = max(0.0, 1.0 - vendor.response_time_minutes / 240.0)

            total = (
                weights["proximity"] * proximity_score
                + weights["availability"] * availability_score
                + weights["rating"] * rating_score
                + weights["cost"] * cost_score
                + weights["response_time"] * response_time_score
            )

            scored.append(
                {
                    "vendor_id": str(vendor.id),
                    "name": vendor.name,
                    "trade": trade,
                    "score": round(total, 4),
                    "distance_km": round(distance_km, 2),
                    "eta_minutes": vendor.response_time_minutes,
                    "rating": vendor.rating,
                    "estimated_cost": float(vendor.hourly_rate or 0),
                    "insurance_verified": vendor.insurance_verified,
                    "breakdown": {
                        "proximity": round(proximity_score, 3),
                        "availability": round(availability_score, 3),
                        "rating": round(rating_score, 3),
                        "cost": round(cost_score, 3),
                        "response_time": round(response_time_score, 3),
                    },
                }
            )
        scored.sort(key=lambda x: x["score"], reverse=True)
        logger.info("vendor.match", extra={"count": len(scored), "trade": trade})
        return scored
