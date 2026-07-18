# Waji Case Data Contract

Raw evidence is immutable. A correction creates a new version linked to the prior record; derived data links to raw object URI, SHA-256, protocol version, and processing version.

## FaultEvent

Required: `event_id`, `machine_id`, make, model, fleet/serial ID, hours, opened_at, location, reporter, trigger, symptom description, recent repair, attachment, environment, work_order_id, status, and provenance.

## Capture

Required: `capture_id`, `event_id`, raw object URI, SHA-256, captured_at, device ID/version, sensor ID/version, component, position photo, position text, distance, direction/orientation, coupling, enclosure state, action, load, duration, sample rate, channels, gain mode, environment, quality status/reasons, repeat index, operator, protocol version, and related pre/post capture IDs.

## Observation

Required: `observation_id`, `event_id`, source capture or inspection ID, statement, units when measured, author, observed_at, provenance, and quality status.

## Hypothesis

Required: `hypothesis_id`, `event_id`, suspected component, suspected failure mode, proposer, supporting Observation IDs, contradicting Observation IDs, alternatives, confidence, missing evidence, safest next verification, technician voice source when used, rule/case/model version, and status.

## Decision

Required: `decision_id`, `event_id`, decision, decider, decided_at, evidence IDs, urgency, risk, authority basis, reversibility, rollback action, work_order_id, and status.

## Outcome

Required: `outcome_id`, `event_id`, established_by, established_at, disposition, confirmed or excluded component, failure mode, inspection/test evidence, parts, adjustments, work_order_id, post-capture IDs, before/after comparison, residual uncertainty, and closure status.

## Completeness

```text
complete = event + valid raw capture + context + hypothesis + decision + outcome or unresolved disposition
verified_complete = complete + comparable follow-up capture
```

An unresolved disposition states missing evidence, next review condition, owner, and due date. A technician voice note remains provenance for a Hypothesis; it is not an Outcome by itself.
