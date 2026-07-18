# Evidence Model

Keep the four record types separate and append-only. Corrections create a new version linked to the superseded record.

## Observation

Required fields: `observation_id`, `case_id`, `source_type`, `source_id`, `captured_at`, `raw_evidence_uri`, `sha256`, `protocol_version`, `context`, `quality_status`, `author`, and `created_at`.

An Observation states what was measured, heard, seen, read, or reported. It does not state the cause.

## Hypothesis

Required fields: `hypothesis_id`, `case_id`, `statement`, `proposer`, `supporting_observation_ids`, `contradicting_observation_ids`, `alternative_explanations`, `confidence`, `missing_evidence`, `verification_action`, `rule_case_or_model_version`, `status`, and timestamps.

Valid status values: `open`, `supported`, `weakened`, `rejected`, `superseded`. A Hypothesis never becomes an Outcome by editing its type.

## Decision

Required fields: `decision_id`, `case_id`, `decision`, `decider`, `decided_at`, `evidence_ids`, `risk`, `authority_basis`, `reversibility`, `rollback_action`, `urgency`, and `status`.

High-impact actions require named human authority and, where relevant, an independent safety control.

## Outcome

Required fields: `outcome_id`, `case_id`, `outcome_type`, `established_by`, `established_at`, `inspection_or_repair_record`, `confirmed_or_excluded_component`, `failure_mode`, `parts_or_adjustments`, `post_observation_ids`, `comparison_result`, `residual_uncertainty`, and `closure_status`.

Valid closure status values: `verified`, `partially_verified`, `excluded`, `unresolved`, `reopened`.

## Integrity and dissent

- Preserve raw evidence, checksum, acquisition context, protocol version, and original author.
- Preserve model and human outputs as separate records.
- Record disagreements explicitly; do not overwrite the losing interpretation.
- Link every derived feature and result to immutable raw evidence and a processing version.
- Close a case only with an Outcome or an explicit unresolved disposition and next review condition.
- Reopening creates a new event linked to the prior case.
