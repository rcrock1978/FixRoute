"""Initial Vendor migration."""
from __future__ import annotations

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = [("intake", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Vendor",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, serialize=False)),
                ("tenant_id", models.UUIDField(db_index=True)),
                ("name", models.CharField(max_length=255)),
                ("trades", models.JSONField(default=list, help_text="List of trade specialties")),
                ("coverage_areas", models.JSONField(default=list, help_text="Postal codes / geographic coverage")),
                ("availability", models.JSONField(default=dict, help_text="Schedule by day-of-week")),
                ("rating", models.FloatField(default=0.0)),
                ("contact_email", models.EmailField(max_length=254)),
                ("contact_phone", models.CharField(max_length=32)),
                ("insurance_verified", models.BooleanField(default=False)),
                ("response_time_minutes", models.IntegerField(default=60)),
                ("hourly_rate", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("apns_token", models.CharField(blank=True, default="", max_length=255)),
                ("fcm_token", models.CharField(blank=True, default="", max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "vendors"},
        ),
        migrations.AddIndex(
            model_name="vendor",
            index=models.Index(fields=["tenant_id"], name="vendor_tenant_idx"),
        ),
        migrations.CreateModel(
            name="CostEstimate",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, serialize=False)),
                ("tenant_id", models.UUIDField(db_index=True)),
                ("dispatch_id", models.UUIDField(db_index=True)),
                ("line_items", models.JSONField(default=list)),
                ("total", models.DecimalField(decimal_places=2, max_digits=10)),
                ("variance", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("status", models.CharField(
                    choices=[("pending", "Pending"), ("approved", "Approved"),
                             ("rejected", "Rejected"), ("revised", "Revised")],
                    db_index=True, default="pending", max_length=16,
                )),
                ("approved_by_id", models.UUIDField(blank=True, null=True)),
                ("approved_at", models.DateTimeField(blank=True, null=True)),
                ("review_comment", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "cost_estimates"},
        ),
        migrations.AddIndex(
            model_name="costestimate",
            index=models.Index(fields=["tenant_id", "status"], name="ce_tenant_status_idx"),
        ),
    ]
