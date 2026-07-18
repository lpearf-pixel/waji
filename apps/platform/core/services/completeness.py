from __future__ import annotations

from dataclasses import dataclass

from core.models import Capture, FaultEvent, Outcome

VALID_QUALITY_STATES = {
    Capture.QualityStatus.VALID,
    Capture.QualityStatus.USABLE_WITH_NOISE,
}


@dataclass(frozen=True)
class CompletenessResult:
    status: str
    missing: tuple[str, ...]


def _has_capture_context(capture: Capture) -> bool:
    return bool(capture.component.strip() and capture.position_text.strip() and capture.action.strip())


def _has_explicit_unresolved_disposition(event: FaultEvent) -> bool:
    return bool(
        event.unresolved_reason.strip()
        and event.unresolved_next_condition.strip()
        and event.unresolved_owner_id
        and event.unresolved_due_date
    )


def evaluate_event_completeness(event: FaultEvent) -> CompletenessResult:
    missing: list[str] = []
    pre_captures = list(
        event.captures.filter(stage=Capture.Stage.PRE, quality_status__in=VALID_QUALITY_STATES)
    )
    if not pre_captures:
        missing.append("pre_capture")
    elif not any(_has_capture_context(capture) for capture in pre_captures):
        missing.append("capture_context")

    if not event.hypotheses.exists():
        missing.append("hypothesis")
    if not event.decisions.exists():
        missing.append("decision")

    try:
        outcome_exists = bool(event.outcome)
    except Outcome.DoesNotExist:
        outcome_exists = False
    if not outcome_exists and not _has_explicit_unresolved_disposition(event):
        missing.append("outcome_or_unresolved")

    core_missing = tuple(missing)
    if core_missing:
        return CompletenessResult(status="incomplete", missing=core_missing)

    has_post_capture = event.captures.filter(
        stage=Capture.Stage.POST,
        quality_status__in=VALID_QUALITY_STATES,
    ).exists()
    if not has_post_capture:
        return CompletenessResult(status="complete", missing=("post_capture",))
    return CompletenessResult(status="verified_complete", missing=())
