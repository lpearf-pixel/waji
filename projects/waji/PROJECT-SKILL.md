# Waji Project Skill

**REQUIRED PARENT SKILL:** `skills/engineering-machinery-health-systems/SKILL.md`

Read the parent skill first. This file supplies Waji-specific boundaries; it does not replace the parent workflow.

## Mission

Waji starts with **故障触发式现场采集**: when a machine presents an abnormal sound, performance decline, or suspected fault, a technician uses a phone or portable device to capture evidence under a repeatable protocol. **人工判断** remains authoritative for inspection and repair. The case closes only through an inspection or repair result and, when feasible, a comparable follow-up capture.

## Initial non-goals

- No fleet-wide fixed edge deployment or continuous monitoring.
- No automatic alarm, shutdown, disassembly, or parts replacement.
- No CAN transmission from the capture tool.
- No voice-only confirmed diagnosis.
- No fault-accuracy marketing from a small case set.
- No replacement of original service procedures, pressure tests, oil analysis, fault codes, or qualified technicians.

## Product route

Use this order and do not skip gates:

1. **故障触发式现场采集** — phone-first protocol, technician notes, inspection or repair outcome, and follow-up capture.
2. **低成本便携终端** — a technician-carried, battery-powered, modular tool with a design BOM target of **人民币 1,000–2,500 元**.
3. **固定边缘** — only after **Gate 5** proves a persistent high-value precursor, insufficient human capture, and positive lifecycle economics.

A portable terminal does not naturally or automatically lead to fixed edge monitoring.

## Evidence and authority

Store `Observation`, `Hypothesis`, `Decision`, and `Outcome` separately. A master's listening judgment, case similarity, spectrum, rule, or model output is a `Hypothesis` until inspection, testing, repair, exclusion, or repeatable follow-up evidence establishes an `Outcome`.

High-impact actions remain human-authorized. Preserve contradictory evidence, reviewer identity, original records, versions, and rollback.

## Required Waji references

Read the relevant reference before designing or implementing its area:

- `references/fault-triggered-field-capture.md`
- `references/low-cost-portable-terminal.md`
- `references/sensor-installation-contract.md`
- `references/data-contract.md`
- `references/diagnosis-review-contract.md`
- `references/validation-gates.md`

## Required output additions

In addition to the parent blueprint, every Waji proposal states:

- current Gate 0–7 status;
- why phone, portable terminal, or fixed edge is the minimum sufficient route;
- field safety and qualified-operator boundary;
- complete-case and verified-complete definitions;
- technician workload and expected maintenance value;
- evidence that blocks or permits hardware escalation.
