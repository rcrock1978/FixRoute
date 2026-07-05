"""URL routing for analytics, estimates, and dispatch-related endpoints."""
from __future__ import annotations

from django.urls import path

from backend.apps.analytics.api.views import spend_analytics
from backend.apps.dispatch.api.estimate_views import review_estimate, submit_estimate

urlpatterns = [
    path("analytics/spend/", spend_analytics, name="spend-analytics"),
    path("dispatches/<uuid:dispatch_id>/estimate/", submit_estimate, name="submit-estimate"),
    path("estimates/<uuid:estimate_id>/approve/", review_estimate, name="review-estimate"),
]
