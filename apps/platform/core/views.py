from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .forms import (
    CaptureForm,
    DecisionForm,
    FaultEventForm,
    HypothesisForm,
    MachineForm,
    ObservationForm,
    OutcomeForm,
    UnresolvedDispositionForm,
)
from .models import Capture, FaultEvent, Machine, Outcome
from .services.audio_processing import process_capture_audio
from .services.completeness import evaluate_event_completeness


@api_view(["GET"])
def health(request):
    return Response({"service": "platform", "status": "ok"})


@login_required
def field_dashboard(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "core/dashboard.html",
        {
            "machines": Machine.objects.filter(active=True).order_by("fleet_id")[:100],
            "events": FaultEvent.objects.select_related("machine", "reporter").all()[:50],
        },
    )


@login_required
def machine_create(request: HttpRequest) -> HttpResponse:
    form = MachineForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        machine = form.save()
        messages.success(request, f"设备 {machine.fleet_id} 已创建。")
        return redirect("field-dashboard")
    return render(request, "core/machine_form.html", {"form": form})


@login_required
def event_create(request: HttpRequest) -> HttpResponse:
    form = FaultEventForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        event = form.save(commit=False)
        event.reporter = request.user
        event.save()
        messages.success(request, "故障事件已创建；当前仅表示触发原因，不代表已确认故障。")
        return redirect("event-detail", public_id=event.public_id)
    return render(request, "core/event_form.html", {"form": form})


@login_required
def event_detail(request: HttpRequest, public_id) -> HttpResponse:
    event = get_object_or_404(
        FaultEvent.objects.select_related("machine", "reporter", "unresolved_owner"),
        public_id=public_id,
    )
    completeness = evaluate_event_completeness(event)
    status_labels = {
        "incomplete": "不完整",
        "complete": "完整（待复测）",
        "verified_complete": "验证完整",
    }
    try:
        outcome = event.outcome
    except Outcome.DoesNotExist:
        outcome = None
    return render(
        request,
        "core/event_detail.html",
        {
            "event": event,
            "captures": event.captures.select_related("operator", "related_pre_capture").all(),
            "observations": event.observations.select_related("author", "capture").all(),
            "hypotheses": event.hypotheses.select_related("proposer").all(),
            "decisions": event.decisions.select_related("decider").all(),
            "outcome": outcome,
            "completeness": completeness,
            "completeness_label": status_labels[completeness.status],
        },
    )


@login_required
def capture_create(request: HttpRequest, public_id) -> HttpResponse:
    event = get_object_or_404(FaultEvent.objects.select_related("machine"), public_id=public_id)
    form = CaptureForm(request.POST or None, request.FILES or None, event=event)
    if request.method == "POST" and form.is_valid():
        uploaded = request.FILES["raw_file"]
        with transaction.atomic():
            capture = form.save(commit=False)
            capture.event = event
            capture.operator = request.user
            capture.original_filename = uploaded.name
            capture.content_type = getattr(uploaded, "content_type", "") or "application/octet-stream"
            capture.quality_status = Capture.QualityStatus.REVIEW_REQUIRED
            capture.save()
        ambient = (
            event.captures.filter(stage=Capture.Stage.AMBIENT)
            .exclude(pk=capture.pk)
            .order_by("-created_at")
            .first()
        )
        try:
            process_capture_audio(capture, ambient_capture=ambient)
            capture.refresh_from_db()
            if capture.processing_status == "completed":
                messages.success(request, "原始录音已保存，并生成轻度去噪试听副本。")
            else:
                messages.warning(request, "原始录音已保存；派生处理未完成，请查看处理状态。")
        except Exception:
            messages.warning(request, "原始录音已安全保存；派生处理发生异常，可稍后重新处理。")
        return redirect("event-detail", public_id=event.public_id)
    return render(
        request,
        "core/simple_form.html",
        {
            "form": form,
            "title": "上传现场录音",
            "event": event,
            "safety_notice": "录音人员不得进入回转、行走、属具、风扇、皮带、高温和高压危险区域。",
        },
    )


@login_required
def observation_create(request: HttpRequest, public_id) -> HttpResponse:
    event = get_object_or_404(FaultEvent, public_id=public_id)
    form = ObservationForm(request.POST or None, event=event)
    if request.method == "POST" and form.is_valid():
        observation = form.save(commit=False)
        observation.event = event
        observation.author = request.user
        observation.save()
        messages.success(request, "客观观察已保存。")
        return redirect("event-detail", public_id=event.public_id)
    return render(request, "core/simple_form.html", {"form": form, "title": "新增 Observation", "event": event})


@login_required
def hypothesis_create(request: HttpRequest, public_id) -> HttpResponse:
    event = get_object_or_404(FaultEvent, public_id=public_id)
    form = HypothesisForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        hypothesis = form.save(commit=False)
        hypothesis.event = event
        hypothesis.proposer = request.user
        hypothesis.save()
        messages.success(request, "诊断方向已按 Hypothesis 保存，仍需检查或维修结果验证。")
        return redirect("event-detail", public_id=event.public_id)
    return render(request, "core/simple_form.html", {"form": form, "title": "新增 Hypothesis", "event": event})


@login_required
def decision_create(request: HttpRequest, public_id) -> HttpResponse:
    event = get_object_or_404(FaultEvent, public_id=public_id)
    form = DecisionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        decision = form.save(commit=False)
        decision.event = event
        decision.decider = request.user
        decision.save()
        messages.success(request, "人工授权决定已保存。")
        return redirect("event-detail", public_id=event.public_id)
    return render(request, "core/simple_form.html", {"form": form, "title": "新增 Decision", "event": event})


@login_required
def outcome_edit(request: HttpRequest, public_id) -> HttpResponse:
    event = get_object_or_404(FaultEvent, public_id=public_id)
    try:
        instance = event.outcome
    except Outcome.DoesNotExist:
        instance = None
    form = OutcomeForm(request.POST or None, instance=instance, event=event)
    if request.method == "POST" and form.is_valid():
        outcome = form.save(commit=False)
        outcome.event = event
        if instance is None:
            outcome.established_by = request.user
        outcome.save()
        form.save_m2m()
        event.workflow_status = FaultEvent.WorkflowStatus.CLOSED if outcome.closure_status == "closed" else FaultEvent.WorkflowStatus.REPAIRED
        event.save(update_fields=["workflow_status", "updated_at"])
        messages.success(request, "Outcome 已保存；确认内容必须有检查、维修、排除或复测证据支持。")
        return redirect("event-detail", public_id=event.public_id)
    return render(request, "core/simple_form.html", {"form": form, "title": "记录 Outcome", "event": event})


@login_required
def unresolved_edit(request: HttpRequest, public_id) -> HttpResponse:
    event = get_object_or_404(FaultEvent, public_id=public_id)
    form = UnresolvedDispositionForm(request.POST or None, instance=event)
    if request.method == "POST" and form.is_valid():
        event = form.save(commit=False)
        event.workflow_status = FaultEvent.WorkflowStatus.UNRESOLVED
        event.save()
        messages.success(request, "未解决状态已保存，必须按负责人和日期继续复核。")
        return redirect("event-detail", public_id=event.public_id)
    return render(request, "core/simple_form.html", {"form": form, "title": "记录未解决状态", "event": event})
