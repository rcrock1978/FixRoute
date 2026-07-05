"""Initial Dispatch migration."""
from __future__ import annotations

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("intake", "0001_initial"),
        ("vendormanagement", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Dispatch",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, serialize=False)),
                ("status", models.CharField(
                    choices=[
                        ("pending", "Pending"),
                        ("assigned", "Assigned"),
                        ("accepted", "Accepted"),
                        ("en_route", "En Route"),
                        ("on_site", "On Site"),
                        ("completed", "Completed"),
                        ("cancelled", "Cancelled"),
                    ],
                    db_index=True,
                    default="assigned",
                    max_length=16,
                )),
                ("estimated_cost", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("final_cost", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("estimated_arrival_at", models.DateTimeField(blank=True, null=True)),
                ("actual_arrival_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("notes", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("work_order", models.ForeignKey(on_delete=models.deletion.PROTECT, related_name="dispatches", to="intake.workorder")),
                ("vendor", models.ForeignKey(on_delete=models.deletion.PROTECT, related_name="dispatches", to="vendormanagement.vendor")),
            ],
            options={"db_table": "dispatches"},
        ),
        migrations.AddIndex(
            model_name="dispatch",
            index=models.Index(fields=["vendor", "status"], name="dispatch_vendor_status_idx"),
        ),
        migrations.AddIndex(
            model_name="dispatch",
            index=models.Index(fields=["work_order"], name="dispatch_wo_idx"),
        ),
    ]
