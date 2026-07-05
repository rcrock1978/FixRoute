"""URL configuration — versioned API at /api/v1/."""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("backend.apps.intake.api.urls")),
    path("api/v1/", include("backend.apps.triage.api.urls")),
    path("api/v1/", include("backend.apps.dispatch.api.urls")),
    path("api/v1/", include("backend.apps.vendormanagement.api.urls")),
    path("api/v1/", include("backend.apps.analytics.api.urls")),
    path("api/v1/", include("backend.apps.compliance.api.urls")),
    path("api/v1/", include("backend.apps.operations.api.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
