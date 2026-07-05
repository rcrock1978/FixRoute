"""Permission classes — IsTenantMember enforces role-based access per FR-013."""
from __future__ import annotations

from rest_framework.permissions import BasePermission

ROLE_HIERARCHY = {
    "tenant": 0,
    "vendor": 0,
    "maintenance_coordinator": 1,
    "property_manager": 2,
}


class IsTenantMember(BasePermission):
    """Allow only authenticated users whose tenant_id matches the request tenant.

    Role hierarchy: property_manager > maintenance_coordinator > tenant/vendor.
    """

    message = "Tenant isolation violation or insufficient role."

    def has_permission(self, request, view) -> bool:
        principal = getattr(request, "user", None)
        if principal is None or not getattr(principal, "is_authenticated", False):
            return False
        principal_tenant = getattr(principal, "tenant_id", None)
        request_tenant = getattr(request, "tenant_id", None)
        if principal_tenant and request_tenant and principal_tenant != request_tenant:
            return False
        required_role = getattr(view, "required_role", None)
        if required_role is None:
            return True
        return ROLE_HIERARCHY.get(getattr(principal, "role", ""), -1) >= ROLE_HIERARCHY.get(
            required_role, 99
        )
