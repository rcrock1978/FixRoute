"""AuditLog migration — append-only across all bounded contexts."""
from __future__ import annotations

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies: list[tuple[str, str]] = []

    operations = [
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, serialize=False)),
                ("tenant_id", models.UUIDField(db_index=True)),
                ("actor_id", models.UUIDField(blank=True, null=True)),
                (
                    "actor_role",
                    models.CharField(
                        choices=[
                            ("tenant", "Tenant"),
                            ("property_manager", "Property Manager"),
                            ("maintenance_coordinator", "Maintenance Coordinator"),
                            ("vendor", "Vendor"),
                            ("system", "System"),
                        ],
                        max_length=64,
                    ),
                ),
                ("action", models.CharField(db_index=True, max_length=128)),
                ("entity_type", models.CharField(db_index=True, max_length=64)),
                ("entity_id", models.UUIDField(db_index=True)),
                ("previous_state", models.JSONField(blank=True, null=True)),
                ("new_state", models.JSONField(blank=True, null=True)),
                ("is_tombstone", models.BooleanField(default=False)),
                ("timestamp", models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={"db_table": "audit_logs", "ordering": ["-timestamp"]},
        ),
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(
                fields=["tenant_id", "entity_type", "entity_id"], name="audit_entity_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(fields=["timestamp"], name="audit_time_idx"),
        ),
    ]
