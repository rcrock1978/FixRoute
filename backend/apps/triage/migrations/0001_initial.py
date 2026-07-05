"""TriageResult migration — 1:1 to WorkOrder."""
from __future__ import annotations

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    initial = True
    dependencies = [("intake", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="TriageResult",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, serialize=False)),
                ("category", models.CharField(max_length=32)),
                ("urgency", models.CharField(max_length=16)),
                ("confidence", models.FloatField()),
                ("troubleshooting_steps", models.JSONField(blank=True, default=list)),
                ("ai_model_version", models.CharField(max_length=64)),
                ("classification_time_ms", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "work_order",
                    models.OneToOneField(
                        on_delete=models.deletion.CASCADE,
                        related_name="triage_result",
                        to="intake.workorder",
                    ),
                ),
            ],
            options={"db_table": "triage_results"},
        ),
    ]
