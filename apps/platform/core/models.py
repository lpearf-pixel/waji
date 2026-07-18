from __future__ import annotations

import uuid
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

ALLOWED_AUDIO_EXTENSIONS = {".wav", ".m4a", ".mp3", ".aac", ".ogg", ".3gp"}
MAX_AUDIO_BYTES = 100 * 1024 * 1024


def _safe_suffix(filename: str, *, default: str = "") -> str:
    suffix = Path(filename).suffix.lower()
    return suffix if suffix and len(suffix) <= 10 else default


def capture_audio_path(instance: "Capture", filename: str) -> str:
    suffix = _safe_suffix(filename, default=".bin")
    return (
        f"machines/{instance.event.machine.public_id}/events/{instance.event.public_id}/"
        f"audio/{instance.public_id}{suffix}"
    )


def processed_audio_path(instance: "Capture", filename: str) -> str:
    return (
        f"machines/{instance.event.machine.public_id}/events/{instance.event.public_id}/"
        f"processed/{instance.public_id}.wav"
    )


def position_photo_path(instance: "Capture", filename: str) -> str:
    suffix = _safe_suffix(filename, default=".jpg")
    return (
        f"machines/{instance.event.machine.public_id}/events/{instance.event.public_id}/"
        f"photos/{instance.public_id}{suffix}"
    )


class Machine(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    make = models.CharField(max_length=80)
    model = models.CharField(max_length=80)
    fleet_id = models.CharField(max_length=80, unique=True)
    serial_number = models.CharField(max_length=120, blank=True)
    hours = models.PositiveBigIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["fleet_id"]

    def __str__(self) -> str:
        return f"{self.fleet_id} · {self.make} {self.model}"


class FaultEvent(models.Model):
    class Trigger(models.TextChoices):
        ABNORMAL_SOUND = "abnormal_sound", "异响"
        WEAK_ACTION = "weak_action", "动作无力"
        OVERHEATING = "overheating", "过热"
        LEAKAGE = "leakage", "泄漏"
        FAULT_CODE = "fault_code", "故障码"
        INTERMITTENT = "intermittent", "间歇异常"
        POST_REPAIR = "post_repair", "维修后验证"
        COMPARATIVE = "comparative_inspection", "计划对比检查"

    class WorkflowStatus(models.TextChoices):
        OPEN = "open", "待采集"
        INVESTIGATING = "investigating", "调查中"
        REPAIRED = "repaired", "已维修待复测"
        UNRESOLVED = "unresolved", "未解决"
        CLOSED = "closed", "已关闭"

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    machine = models.ForeignKey(Machine, on_delete=models.PROTECT, related_name="events")
    trigger = models.CharField(max_length=40, choices=Trigger.choices)
    symptom = models.TextField()
    location = models.CharField(max_length=200)
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="reported_fault_events")
    opened_at = models.DateTimeField(default=timezone.now)
    recent_repair = models.TextField(blank=True)
    attachment = models.CharField(max_length=160, blank=True)
    environment_notes = models.TextField(blank=True)
    work_order_id = models.CharField(max_length=120, blank=True)
    workflow_status = models.CharField(max_length=30, choices=WorkflowStatus.choices, default=WorkflowStatus.OPEN)
    unresolved_reason = models.TextField(blank=True)
    unresolved_next_condition = models.TextField(blank=True)
    unresolved_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="unresolved_fault_events",
        null=True,
        blank=True,
    )
    unresolved_due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-opened_at", "-created_at"]

    def __str__(self) -> str:
        return f"{self.machine.fleet_id} · {self.get_trigger_display()} · {self.public_id}"


class Capture(models.Model):
    class Stage(models.TextChoices):
        AMBIENT = "ambient", "环境声"
        PRE = "pre", "维修前"
        POST = "post", "维修后"

    class QualityStatus(models.TextChoices):
        VALID = "valid", "有效"
        USABLE_WITH_NOISE = "usable_with_noise", "有杂音但可用"
        REVIEW_REQUIRED = "review_required", "需要复核"
        INVALID_CLIPPING = "invalid_clipping", "削波无效"
        INVALID_SILENCE = "invalid_silence", "静音无效"
        INVALID_DECODE = "invalid_decode", "无法解码"

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    event = models.ForeignKey(FaultEvent, on_delete=models.CASCADE, related_name="captures")
    stage = models.CharField(max_length=20, choices=Stage.choices)
    raw_file = models.FileField(upload_to=capture_audio_path, max_length=500)
    original_filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=120, blank=True)
    raw_sha256 = models.CharField(max_length=64, blank=True, editable=False)
    device_label = models.CharField(max_length=160)
    component = models.CharField(max_length=160)
    position_photo = models.FileField(upload_to=position_photo_path, max_length=500, null=True, blank=True)
    position_text = models.CharField(max_length=255)
    distance_m = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    direction = models.CharField(max_length=255, blank=True)
    enclosure_state = models.CharField(max_length=120, blank=True)
    action = models.CharField(max_length=255)
    load = models.CharField(max_length=160, blank=True)
    displayed_rpm = models.PositiveIntegerField(null=True, blank=True)
    gain_mode = models.CharField(max_length=120, blank=True)
    repeat_index = models.PositiveSmallIntegerField(default=1)
    manual_noise_reasons = models.JSONField(default=list, blank=True)
    quality_status = models.CharField(
        max_length=40,
        choices=QualityStatus.choices,
        default=QualityStatus.REVIEW_REQUIRED,
    )
    quality_reasons = models.JSONField(default=list, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)
    sample_rate = models.PositiveIntegerField(null=True, blank=True)
    channels = models.PositiveSmallIntegerField(null=True, blank=True)
    protocol_version = models.CharField(max_length=40, default="gate0-v1")
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="captures")
    related_pre_capture = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="follow_up_captures",
        null=True,
        blank=True,
    )
    processing_status = models.CharField(max_length=80, default="pending")
    processed_file = models.FileField(upload_to=processed_audio_path, max_length=500, null=True, blank=True)
    processed_sha256 = models.CharField(max_length=64, blank=True, editable=False)
    processing_manifest = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at", "repeat_index"]

    def __str__(self) -> str:
        return f"{self.event.machine.fleet_id} · {self.get_stage_display()} · {self.public_id}"

    def clean(self) -> None:
        super().clean()
        if self.raw_file:
            extension = Path(self.original_filename or self.raw_file.name).suffix.lower()
            if extension not in ALLOWED_AUDIO_EXTENSIONS:
                raise ValidationError({"raw_file": f"不支持的音频格式：{extension or '无扩展名'}"})
            size = getattr(self.raw_file, "size", None)
            if size is not None and size > MAX_AUDIO_BYTES:
                raise ValidationError({"raw_file": "单个音频文件不能超过 100 MB"})
        if self.stage == self.Stage.POST and self.related_pre_capture:
            if self.related_pre_capture.event_id != self.event_id:
                raise ValidationError({"related_pre_capture": "维修前后录音必须属于同一故障事件"})

    def save(self, *args, **kwargs) -> None:
        creating = self._state.adding
        if not creating and self.pk:
            previous = type(self).objects.only("raw_file").get(pk=self.pk)
            replacement_is_uncommitted = self.raw_file and not getattr(self.raw_file, "_committed", True)
            if previous.raw_file.name != self.raw_file.name or replacement_is_uncommitted:
                raise ValidationError({"raw_file": "原始录音不可替换；请新建一条采集记录"})
        self.full_clean()
        super().save(*args, **kwargs)
        if creating and self.raw_file and not self.raw_sha256:
            from .services.file_integrity import sha256_storage_file

            digest = sha256_storage_file(self.raw_file)
            type(self).objects.filter(pk=self.pk).update(raw_sha256=digest)
            self.raw_sha256 = digest


class Observation(models.Model):
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    event = models.ForeignKey(FaultEvent, on_delete=models.CASCADE, related_name="observations")
    capture = models.ForeignKey(Capture, on_delete=models.PROTECT, related_name="observations", null=True, blank=True)
    statement = models.TextField()
    units = models.CharField(max_length=80, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="observations")
    observed_at = models.DateTimeField(default=timezone.now)
    provenance = models.CharField(max_length=255)
    quality_status = models.CharField(max_length=40, default="valid")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["observed_at", "created_at"]

    def __str__(self) -> str:
        return self.statement[:80]


class Hypothesis(models.Model):
    class Confidence(models.TextChoices):
        LOW = "low", "低"
        MEDIUM = "medium", "中"
        HIGH = "high", "高"

    class Status(models.TextChoices):
        OPEN = "open", "待验证"
        SUPPORTED = "supported", "证据支持"
        CONTRADICTED = "contradicted", "证据反对"
        CLOSED = "closed", "已关闭"

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    event = models.ForeignKey(FaultEvent, on_delete=models.CASCADE, related_name="hypotheses")
    suspected_component = models.CharField(max_length=160)
    suspected_failure_mode = models.CharField(max_length=255)
    proposer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="hypotheses")
    supporting_evidence = models.TextField()
    contradicting_evidence = models.TextField(blank=True)
    alternatives = models.TextField(blank=True)
    confidence = models.CharField(max_length=20, choices=Confidence.choices)
    missing_evidence = models.TextField(blank=True)
    safest_next_verification = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.suspected_component}: {self.suspected_failure_mode}"


class Decision(models.Model):
    class Urgency(models.TextChoices):
        MONITOR = "monitor", "继续观察"
        SAME_DAY = "same_day", "当天处理"
        IMMEDIATE_SAFE_STOP = "immediate_safe_stop", "由合格人员安全停机"

    class Status(models.TextChoices):
        PROPOSED = "proposed", "建议"
        APPROVED = "approved", "已授权"
        EXECUTED = "executed", "已执行"
        CANCELLED = "cancelled", "已取消"

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    event = models.ForeignKey(FaultEvent, on_delete=models.CASCADE, related_name="decisions")
    decision = models.TextField()
    decider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="decisions")
    decided_at = models.DateTimeField(default=timezone.now)
    urgency = models.CharField(max_length=40, choices=Urgency.choices)
    risk = models.TextField()
    authority_basis = models.TextField()
    reversibility = models.TextField()
    rollback_action = models.TextField()
    work_order_id = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PROPOSED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["decided_at", "created_at"]

    def __str__(self) -> str:
        return self.decision[:80]


class Outcome(models.Model):
    class Disposition(models.TextChoices):
        REPAIRED = "repaired", "维修确认"
        ADJUSTED = "adjusted", "调整确认"
        EXCLUDED = "excluded", "排除"
        NO_FAULT_FOUND = "no_fault_found", "未发现故障"
        DEFERRED = "deferred", "延期复核"

    class ClosureStatus(models.TextChoices):
        OPEN = "open", "待复核"
        CLOSED = "closed", "已关闭"

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    event = models.OneToOneField(FaultEvent, on_delete=models.CASCADE, related_name="outcome")
    established_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="outcomes")
    established_at = models.DateTimeField(default=timezone.now)
    disposition = models.CharField(max_length=40, choices=Disposition.choices)
    confirmed_component = models.CharField(max_length=160, blank=True)
    excluded_component = models.CharField(max_length=160, blank=True)
    failure_mode = models.CharField(max_length=255, blank=True)
    inspection_evidence = models.TextField()
    parts = models.TextField(blank=True)
    adjustments = models.TextField(blank=True)
    before_after_comparison = models.TextField(blank=True)
    residual_uncertainty = models.TextField(blank=True)
    closure_status = models.CharField(max_length=20, choices=ClosureStatus.choices, default=ClosureStatus.OPEN)
    post_captures = models.ManyToManyField(Capture, related_name="outcomes", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.event.public_id} · {self.get_disposition_display()}"
