from django.contrib import admin

from .models import Capture, Decision, FaultEvent, Hypothesis, Machine, Observation, Outcome


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ("fleet_id", "make", "model", "hours", "active", "updated_at")
    search_fields = ("fleet_id", "serial_number", "make", "model")
    readonly_fields = ("public_id", "created_at", "updated_at")


@admin.register(FaultEvent)
class FaultEventAdmin(admin.ModelAdmin):
    list_display = ("public_id", "machine", "trigger", "workflow_status", "reporter", "opened_at")
    list_filter = ("trigger", "workflow_status")
    search_fields = ("public_id", "machine__fleet_id", "symptom", "work_order_id")
    readonly_fields = ("public_id", "created_at", "updated_at")


@admin.register(Capture)
class CaptureAdmin(admin.ModelAdmin):
    list_display = ("public_id", "event", "stage", "quality_status", "processing_status", "operator", "created_at")
    list_filter = ("stage", "quality_status", "processing_status")
    search_fields = ("public_id", "event__machine__fleet_id", "component", "position_text")
    readonly_fields = (
        "public_id",
        "raw_sha256",
        "processed_sha256",
        "processing_manifest",
        "created_at",
        "updated_at",
    )


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    list_display = ("public_id", "event", "author", "observed_at", "quality_status")
    search_fields = ("public_id", "statement", "event__machine__fleet_id")
    readonly_fields = ("public_id", "created_at")


@admin.register(Hypothesis)
class HypothesisAdmin(admin.ModelAdmin):
    list_display = ("public_id", "event", "suspected_component", "confidence", "status", "proposer", "created_at")
    list_filter = ("confidence", "status")
    search_fields = ("public_id", "suspected_component", "suspected_failure_mode", "event__machine__fleet_id")
    readonly_fields = ("public_id", "created_at", "updated_at")


@admin.register(Decision)
class DecisionAdmin(admin.ModelAdmin):
    list_display = ("public_id", "event", "urgency", "status", "decider", "decided_at")
    list_filter = ("urgency", "status")
    search_fields = ("public_id", "decision", "work_order_id", "event__machine__fleet_id")
    readonly_fields = ("public_id", "created_at")


@admin.register(Outcome)
class OutcomeAdmin(admin.ModelAdmin):
    list_display = ("public_id", "event", "disposition", "closure_status", "established_by", "established_at")
    list_filter = ("disposition", "closure_status")
    search_fields = ("public_id", "confirmed_component", "failure_mode", "event__machine__fleet_id")
    readonly_fields = ("public_id", "created_at", "updated_at")
