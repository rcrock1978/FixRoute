"""URL routing for the intake app — exposes work-orders endpoints."""
from __future__ import annotations

from rest_framework.routers import DefaultRouter

from backend.apps.intake.api.views import WorkOrderViewSet

router = DefaultRouter()
router.register(r"work-orders", WorkOrderViewSet, basename="work-order")

urlpatterns = router.urls
