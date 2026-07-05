"""Initial migration: enable pgvector, create Tenant/Property/TenantProfile/WorkOrder/MediaAsset.

Per the post-spec clarify session (T019f), this migration enables the pgvector
extension and creates the HNSW indexes for cosine similarity duplicate detection.
"""
from __future__ import annotations

from django.db import migrations, models
import pgvector.django.vector
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies: list[tuple[str, str]] = []

    operations = [
        migrations.RunSQL(
            sql="CREATE EXTENSION IF NOT EXISTS vector;",
            reverse_sql="DROP EXTENSION IF EXISTS vector;",
        ),
        migrations.CreateModel(
            name="Tenant",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, serialize=False)),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(max_length=64, unique=True)),
                ("settings", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("soft_deleted_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("hard_delete_at", models.DateTimeField(blank=True, db_index=True, null=True)),
            ],
            options={"db_table": "tenants"},
        ),
        migrations.CreateModel(
            name="Property",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, serialize=False)),
                ("tenant_id", models.UUIDField(db_index=True)),
                ("name", models.CharField(max_length=255)),
                ("address", models.TextField()),
                ("unit_count", models.IntegerField(default=1)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "properties"},
        ),
        migrations.CreateModel(
            name="TenantProfile",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, serialize=False)),
                ("tenant_id", models.UUIDField(db_index=True)),
                ("name", models.CharField(max_length=255)),
                ("email", models.EmailField(max_length=254, db_index=True)),
                ("phone", models.CharField(blank=True, default="", max_length=32)),
                ("unit", models.CharField(blank=True, default="", max_length=32)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "property",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="residents",
                        to="intake.property",
                    ),
                ),
            ],
            options={"db_table": "tenant_profiles"},
        ),
        migrations.CreateModel(
            name="WorkOrder",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, serialize=False)),
                ("tenant_id", models.UUIDField(db_index=True)),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("submitted", "Submitted"),
                            ("classified", "Classified"),
                            ("troubleshooting", "Troubleshooting"),
                            ("dispatched", "Dispatched"),
                            ("in_progress", "In Progress"),
                            ("completed", "Completed"),
                        ],
                        db_index=True,
                        default="submitted",
                        max_length=32,
                    ),
                ),
                (
                    "priority",
                    models.CharField(
                        choices=[
                            ("emergency", "Emergency"),
                            ("urgent", "Urgent"),
                            ("routine", "Routine"),
                            ("low", "Low"),
                        ],
                        db_index=True,
                        default="routine",
                        max_length=16,
                    ),
                ),
                (
                    "category",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("plumbing", "Plumbing"),
                            ("electrical", "Electrical"),
                            ("HVAC", "HVAC"),
                            ("structural", "Structural"),
                            ("appliance", "Appliance"),
                            ("general", "General"),
                        ],
                        max_length=32,
                        null=True,
                    ),
                ),
                ("voice_transcript", models.TextField(blank=True, default="")),
                ("description_embedding", pgvector.django.vector.VectorField(blank=True, dimensions=1536, null=True)),
                ("image_embedding", pgvector.django.vector.VectorField(blank=True, dimensions=512, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("soft_deleted_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("hard_delete_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                (
                    "property",
                    models.ForeignKey(
                        on_delete=models.deletion.PROTECT,
                        related_name="work_orders",
                        to="intake.property",
                    ),
                ),
                (
                    "submitted_by",
                    models.ForeignKey(
                        on_delete=models.deletion.PROTECT,
                        related_name="submitted_work_orders",
                        to="intake.tenantprofile",
                    ),
                ),
            ],
            options={"db_table": "work_orders"},
        ),
        migrations.AddIndex(
            model_name="workorder",
            index=models.Index(fields=["tenant_id", "status"], name="wo_tenant_status_idx"),
        ),
        migrations.AddIndex(
            model_name="workorder",
            index=models.Index(fields=["tenant_id", "-created_at"], name="wo_tenant_recent_idx"),
        ),
        migrations.AddIndex(
            model_name="workorder",
            index=models.Index(fields=["property", "status"], name="wo_property_status_idx"),
        ),
        # HNSW indexes for pgvector cosine similarity duplicate detection
        migrations.RunSQL(
            sql=(
                "CREATE INDEX IF NOT EXISTS workorder_description_embedding_idx "
                "ON work_orders USING hnsw (description_embedding vector_cosine_ops) "
                "WHERE description_embedding IS NOT NULL;"
            ),
            reverse_sql="DROP INDEX IF EXISTS workorder_description_embedding_idx;",
        ),
        migrations.RunSQL(
            sql=(
                "CREATE INDEX IF NOT EXISTS workorder_image_embedding_idx "
                "ON work_orders USING hnsw (image_embedding vector_cosine_ops) "
                "WHERE image_embedding IS NOT NULL;"
            ),
            reverse_sql="DROP INDEX IF EXISTS workorder_image_embedding_idx;",
        ),
        migrations.CreateModel(
            name="MediaAsset",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, serialize=False)),
                ("tenant_id", models.UUIDField(db_index=True)),
                ("blob_url", models.CharField(max_length=512)),
                ("container", models.CharField(max_length=128)),
                (
                    "tier",
                    models.CharField(
                        choices=[("hot", "Hot"), ("cool", "Cool"), ("archive", "Archive")],
                        default="hot",
                        max_length=16,
                    ),
                ),
                ("content_type", models.CharField(max_length=64)),
                ("size_bytes", models.BigIntegerField(blank=True, null=True)),
                ("checksum_sha256", models.CharField(blank=True, default="", max_length=64)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("soft_deleted_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("hard_delete_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                (
                    "work_order",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="media",
                        to="intake.workorder",
                    ),
                ),
            ],
            options={"db_table": "media_assets"},
        ),
    ]
