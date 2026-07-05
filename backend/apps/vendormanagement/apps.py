from django.apps import AppConfig


class VendorManagementConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "backend.apps.vendormanagement"
    label = "vendormanagement"
    verbose_name = "Vendor Management"
