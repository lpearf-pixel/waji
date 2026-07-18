# Generated for the Gate 0 field-capture MVP.

import uuid

import core.models
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Machine",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("public_id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("make", models.CharField(max_length=80)),
                ("model", models.CharField(max_length=80)),
                ("fleet_id", models.CharField(max_length=80, unique=True)),
                ("serial_number", models.CharField(blank=True, max_length=120)),
                ("hours", models.PositiveBigIntegerField(default=0)),
                ("active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["fleet_id"]},
        ),
        migrations.CreateModel(
            name="FaultEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("public_id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                (
                    "trigger",
                    models.CharField(
                        choices=[
                            ("abnormal_sound", "异响"),
                            ("weak_action", "动作无力"),
                            ("overheating", "过热"),
                            ("leakage", "泄漏"),
                            ("fault_code", "故障码"),
                            ("intermittent", "间歇异常"),
                            ("post_repair", "维修后验证"),
                            ("comparative_inspection", "计划对比检查"),
                        ],
                        max_length=40,
                    ),
                ),
                ("symptom", models.TextField()),
                ("location", models.CharField(max_length=200)),
                ("opened_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("recent_repair", models.TextField(blank=True)),
                ("attachment", models.CharField(blank=True, max_length=160)),
                ("environment_notes", models.TextField(blank=True)),
                ("work_order_id", models.CharField(blank=True, max_length=120)),
                (
                    "workflow_status",
                    models.CharField(
                        choices=[
                            ("open", "待采集"),
                            ("investigating", "调查中"),
                            ("repaired", "已维修待复测"),
                            ("unresolved", "未解决"),
                            ("closed", "已关闭"),
                        ],
                        default="open",
                        max_length=30,
                    ),
                ),
                ("unresolved_reason", models.TextField(blank=True)),
                ("unresolved_next_condition", models.TextField(blank=True)),
                ("unresolved_due_date", models.DateField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "machine",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="events", to="core.machine"),
                ),
                (
                    "reporter",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="reported_fault_events",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "unresolved_owner",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="unresolved_fault_events",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-opened_at", "-created_at"]},
        ),
        migrations.CreateModel(
            name="Capture",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("public_id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                (
                    "stage",
                    models.CharField(
                        choices=[("ambient", "环境声"), ("pre", "维修前"), ("post", "维修后")],
                        max_length=20,
                    ),
                ),
                ("raw_file", models.FileField(upload_to=core.models.capture_audio_path)),
                ("original_filename", models.CharField(max_length=255)),
                ("content_type", models.CharField(blank=True, max_length=120)),
                ("raw_sha256", models.CharField(blank=True, editable=False, max_length=64)),
                ("device_label", models.CharField(max_length=160)),
                ("component", models.CharField(max_length=160)),
                ("position_photo", models.FileField(blank=True, null=True, upload_to=core.models.position_photo_path)),
                ("position_text", models.CharField(max_length=255)),
                ("distance_m", models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ("direction", models.CharField(blank=True, max_length=255)),
                ("enclosure_state", models.CharField(blank=True, max_length=120)),
                ("action", models.CharField(max_length=255)),
                ("load", models.CharField(blank=True, max_length=160)),
                ("displayed_rpm", models.PositiveIntegerField(blank=True, null=True)),
                ("gain_mode", models.CharField(blank=True, max_length=120)),
                ("repeat_index", models.PositiveSmallIntegerField(default=1)),
                ("manual_noise_reasons", models.JSONField(blank=True, default=list)),
                (
                    "quality_status",
                    models.CharField(
                        choices=[
                            ("valid", "有效"),
                            ("usable_with_noise", "有杂音但可用"),
                            ("review_required", "需要复核"),
                            ("invalid_clipping", "削波无效"),
                            ("invalid_silence", "静音无效"),
                            ("invalid_decode", "无法解码"),
                        ],
                        default="review_required",
                        max_length=40,
                    ),
                ),
                ("quality_reasons", models.JSONField(blank=True, default=list)),
                ("duration_seconds", models.FloatField(blank=True, null=True)),
                ("sample_rate", models.PositiveIntegerField(blank=True, null=True)),
                ("channels", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("protocol_version", models.CharField(default="gate0-v1", max_length=40)),
                ("processing_status", models.CharField(default="pending", max_length=80)),
                ("processed_file", models.FileField(blank=True, null=True, upload_to=core.models.processed_audio_path)),
                ("processed_sha256", models.CharField(blank=True, editable=False, max_length=64)),
                ("processing_manifest", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "event",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="captures", to="core.faultevent"),
                ),
                (
                    "operator",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="captures", to=settings.AUTH_USER_MODEL),
                ),
                (
                    "related_pre_capture",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="follow_up_captures",
                        to="core.capture",
                    ),
                ),
            ],
            options={"ordering": ["created_at", "repeat_index"]},
        ),
        migrations.CreateModel(
            name="Decision",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("public_id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("decision", models.TextField()),
                ("decided_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "urgency",
                    models.CharField(
                        choices=[
                            ("monitor", "继续观察"),
                            ("same_day", "当天处理"),
                            ("immediate_safe_stop", "由合格人员安全停机"),
                        ],
                        max_length=40,
                    ),
                ),
                ("risk", models.TextField()),
                ("authority_basis", models.TextField()),
                ("reversibility", models.TextField()),
                ("rollback_action", models.TextField()),
                ("work_order_id", models.CharField(blank=True, max_length=120)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("proposed", "建议"),
                            ("approved", "已授权"),
                            ("executed", "已执行"),
                            ("cancelled", "已取消"),
                        ],
                        default="proposed",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "decider",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="decisions", to=settings.AUTH_USER_MODEL),
                ),
                (
                    "event",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="decisions", to="core.faultevent"),
                ),
            ],
            options={"ordering": ["decided_at", "created_at"]},
        ),
        migrations.CreateModel(
            name="Hypothesis",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("public_id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("suspected_component", models.CharField(max_length=160)),
                ("suspected_failure_mode", models.CharField(max_length=255)),
                ("supporting_evidence", models.TextField()),
                ("contradicting_evidence", models.TextField(blank=True)),
                ("alternatives", models.TextField(blank=True)),
                (
                    "confidence",
                    models.CharField(choices=[("low", "低"), ("medium", "中"), ("high", "高")], max_length=20),
                ),
                ("missing_evidence", models.TextField(blank=True)),
                ("safest_next_verification", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("open", "待验证"),
                            ("supported", "证据支持"),
                            ("contradicted", "证据反对"),
                            ("closed", "已关闭"),
                        ],
                        default="open",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "event",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="hypotheses", to="core.faultevent"),
                ),
                (
                    "proposer",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="hypotheses", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Observation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("public_id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("statement", models.TextField()),
                ("units", models.CharField(blank=True, max_length=80)),
                ("observed_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("provenance", models.CharField(max_length=255)),
                ("quality_status", models.CharField(default="valid", max_length=40)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "author",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="observations", to=settings.AUTH_USER_MODEL),
                ),
                (
                    "capture",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="observations",
                        to="core.capture",
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="observations", to="core.faultevent"),
                ),
            ],
            options={"ordering": ["observed_at", "created_at"]},
        ),
        migrations.CreateModel(
            name="Outcome",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("public_id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("established_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "disposition",
                    models.CharField(
                        choices=[
                            ("repaired", "维修确认"),
                            ("adjusted", "调整确认"),
                            ("excluded", "排除"),
                            ("no_fault_found", "未发现故障"),
                            ("deferred", "延期复核"),
                        ],
                        max_length=40,
                    ),
                ),
                ("confirmed_component", models.CharField(blank=True, max_length=160)),
                ("excluded_component", models.CharField(blank=True, max_length=160)),
                ("failure_mode", models.CharField(blank=True, max_length=255)),
                ("inspection_evidence", models.TextField()),
                ("parts", models.TextField(blank=True)),
                ("adjustments", models.TextField(blank=True)),
                ("before_after_comparison", models.TextField(blank=True)),
                ("residual_uncertainty", models.TextField(blank=True)),
                (
                    "closure_status",
                    models.CharField(choices=[("open", "待复核"), ("closed", "已关闭")], default="open", max_length=20),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "established_by",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="outcomes", to=settings.AUTH_USER_MODEL),
                ),
                (
                    "event",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="outcome", to="core.faultevent"),
                ),
                ("post_captures", models.ManyToManyField(blank=True, related_name="outcomes", to="core.capture")),
            ],
        ),
    ]
