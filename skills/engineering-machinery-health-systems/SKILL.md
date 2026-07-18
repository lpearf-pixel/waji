---
name: engineering-machinery-health-systems
description: Use when planning, reviewing, validating, rescuing, or scaling engineering-machinery field inspection, fault data collection, maintenance assistance, condition monitoring, predictive maintenance, acoustic diagnosis, vibration diagnosis, portable sensing, edge sensing, or multi-sensor industrial AI systems.
---

# Engineering Machinery Health Systems

## Overview

Treat machinery health as an open socio-technical system. Value comes from a closed evidence loop linking physical observations, human hypotheses, maintenance decisions, and verified outcomes—not from a sensor, model, dashboard, or accuracy score alone.

## When to Use

Use for work combining machines, technicians, field conditions, sensors, data, diagnosis, maintenance, or staged automation. Do not use for an isolated signal-processing utility with fixed inputs and locally verifiable output.

## Maturity Route

Choose the least expensive route that can close the current loop:

1. **Event-triggered field capture:** collect evidence after a symptom or during inspection.
2. **Portable assisted capture:** improve protocol compliance, metadata, quality checks, and case retrieval.
3. **Fixed monitoring:** use persistent sensors only when people cannot capture the precursor in time and lifecycle economics are positive.

The next route is never automatic. Require an evidence gate before increasing hardware, scale, automation, or control authority.

## Required Workflow

1. Define maintenance outcome, beneficiary, unacceptable harm, time horizon, and non-goals.
2. Map actors, machine, environment, dependencies, controlled variables, observations, inferences, and unknowns.
3. Give acquisition, storage, feature extraction, hypothesis generation, review, maintenance action, and outcome validation explicit interfaces.
4. Preserve observations, hypotheses, decisions, and outcomes as different records.
5. Validate the smallest loop reaching inspection or repair outcome and comparable follow-up evidence.
6. Combine technician knowledge, rules, cases, signal processing, statistics, and AI without hiding disagreement.
7. Version protocol, placement, data, features, model, threshold, review, and rollback.
8. Evaluate transfer, calibration, delay, recurrence, cost, safety, workload, and avoided loss.
9. Expand only after a written stage gate passes.
10. Feed failures and counterexamples back into assumptions, protocol, interfaces, and models.

## Evidence Rules

- Observation is traceable evidence, not interpretation.
- Hypothesis records support, contradiction, alternatives, confidence, and verification action.
- Decision records authority, rationale, risk, and reversibility.
- Outcome records what inspection, repair, exclusion, or follow-up established.
- Similarity, anomaly, or expert opinion remains a Hypothesis until validated.
- Preserve dissent; never silently overwrite human or model history.

Read `references/evidence-model.md` before defining schemas or diagnosis workflows.

## Output Contract

Produce a System Engineering Blueprint in this order:

1. Mission and non-goals
2. Stakeholders and system boundary
3. Current maturity route and minimum-sufficiency rationale
4. Context, data flow, and feedback loop
5. Subsystems and interface contracts
6. Observation–Hypothesis–Decision–Outcome model
7. Minimum closed-loop pilot
8. Metrics and validation
9. Human review, escalation, and rollback
10. Risks, unknowns, and reversible decisions
11. Current stage gate and entry evidence

Use `references/system-blueprint-template.md` and `references/stage-gate-template.md`.

## Stage-Gate Rules

A gate states current and target routes, evidence and cost thresholds, safety constraints, owner, review date, rollback, and result. Accuracy, data volume, a demo, or a single case cannot substitute for it.

## Red Flags

Stop when reasoning says: “install everywhere first,” “the expert or model is usually right,” “higher price proves better evidence,” “enough files means closure,” “portable capture naturally leads to fixed monitoring,” “human review disappears later,” or “the dashboard proves maintenance value.”
