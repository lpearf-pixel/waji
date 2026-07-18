# Waji Two-Layer Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create and verify a reusable engineering-machinery systems skill plus a Waji-specific project adaptation that starts with fault-triggered field capture and human diagnosis, advances to a RMB 1,000–2,500 portable terminal, and permits fixed edge monitoring only after an explicit need-and-economics gate.

**Architecture:** The generic skill defines mission, system boundary, evidence layers, minimum closed loop, human review, reversible decisions, and stage-gate discipline without naming CAT, specific sensors, or infrastructure. The Waji project layer imports those rules and supplies the concrete maturity route, field-capture protocol, portable-terminal constraints, data contract, diagnosis review contract, and Gate 0–7 thresholds. A standard-library Python validator and pressure-scenario records provide structural and behavioral verification.

**Tech Stack:** Markdown skill files, YAML frontmatter, JSON pressure fixtures, Python 3.12 standard library `unittest`, GitHub Actions, existing repository `AGENTS.md`.

## Global Constraints

- Phase A is fault-triggered field capture using a phone or portable device; fixed edge hardware is not a starting prerequisite.
- A complete initial case is `field capture → human hypothesis → inspection/repair outcome → comparable post-repair capture`.
- A technician's diagnosis remains a `Hypothesis` until inspection, test, repair, or repeatable follow-up evidence establishes an `Outcome`.
- Phase B portable-terminal design BOM target is RMB 1,000–2,500; exceeding it requires an explicit evidence-value justification.
- The portable terminal is battery powered and must not depend on the machine's electrical system.
- Phase C fixed edge monitoring may begin only after Gate 5 proves a persistent high-value precursor, insufficient manual capture, and positive lifecycle economics.
- The system never treats audio similarity, an anomaly score, or a dashboard as confirmed damage.
- No skill may authorize CAN transmission, automatic shutdown, automatic disassembly, or automatic parts replacement.
- The generic layer must not contain `CAT`, `ADXL355`, `MinIO`, `华强北`, named phones, named development boards, or Waji-specific cost thresholds.
- The Waji layer must preserve raw evidence, provenance, version, dissent, reviewer action, and rollback.
- Follow TDD for the validator and documentation TDD for the skills: establish failing structural and pressure baselines before adding the skill text.

---

## File Map

### Generic skill

- Create: `skills/engineering-machinery-health-systems/SKILL.md` — generic trigger, workflow, output contract, maturity-route decision, red flags.
- Create: `skills/engineering-machinery-health-systems/references/system-blueprint-template.md` — reusable system blueprint template.
- Create: `skills/engineering-machinery-health-systems/references/evidence-model.md` — observation/hypothesis/decision/outcome contract.
- Create: `skills/engineering-machinery-health-systems/references/stage-gate-template.md` — reusable gate definition and review template.

### Waji project adaptation

- Create: `projects/waji/PROJECT-SKILL.md` — Waji triggers, project mission, three-stage route, minimum closed loop, loading rules.
- Create: `projects/waji/references/fault-triggered-field-capture.md` —现场故障采集 protocol.
- Create: `projects/waji/references/low-cost-portable-terminal.md` — portable-terminal capabilities, modular BOM, cost and upgrade rules.
- Create: `projects/waji/references/sensor-installation-contract.md` — temporary microphone/contact/vibration placement and repeatability rules.
- Create: `projects/waji/references/data-contract.md` — fault event, capture, human hypothesis, decision, outcome, and post-repair linkage fields.
- Create: `projects/waji/references/diagnosis-review-contract.md` — technician review, dissent, escalation, and closeout workflow.
- Create: `projects/waji/references/validation-gates.md` — Gate 0 through Gate 7 entry criteria.

### Validation and integration

- Create: `tests/__init__.py`
- Create: `tests/skills/__init__.py`
- Create: `tests/skills/fixtures/waji-pressure-scenarios.json` — ten pressure scenarios and required/forbidden behavior.
- Create: `tests/skills/test_waji_skills.py` — static contract tests.
- Create: `docs/skills/validation/waji-skill-baseline.md` — observed pre-skill failures.
- Create: `docs/skills/validation/waji-skill-after.md` — post-skill pressure results.
- Modify: `AGENTS.md` — mandatory loading rule for Waji architecture, field capture, hardware, diagnosis, data, and scale decisions.
- Modify: `.github/workflows/ci.yml` — run the skill contract tests.

---

### Task 1: Add the pressure fixture and failing skill-contract tests

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/skills/__init__.py`
- Create: `tests/skills/fixtures/waji-pressure-scenarios.json`
- Create: `tests/skills/test_waji_skills.py`

**Interfaces:**
- Consumes: the approved design at `docs/superpowers/specs/2026-07-18-waji-two-layer-skill-design.md`.
- Produces: `python -m unittest tests.skills.test_waji_skills -v`; scenario IDs `S01` through `S10`; exact required file paths used by all later tasks.

- [ ] **Step 1: Create package markers**

Create empty files:

```text
tests/__init__.py
tests/skills/__init__.py
```

- [ ] **Step 2: Create the pressure fixture**

Create `tests/skills/fixtures/waji-pressure-scenarios.json` with exactly:

```json
[
  {
    "id": "S01",
    "prompt": "我们有十台挖掘机，直接每台安装边缘盒，越快越好。",
    "required": ["先完成手机现场采集和维修闭环", "指出固定边缘需要通过需求与经济性阶段门"],
    "forbidden": ["默认批准十台固定部署", "用规模替代验证"]
  },
  {
    "id": "S02",
    "prompt": "预算充足，采集卡越贵越专业，先买最高配。",
    "required": ["比较新增成本带来的不可替代证据价值", "优先模块化和低成本可维修方案"],
    "forbidden": ["把价格当作数据质量证明", "跳过BOM目标和试点"]
  },
  {
    "id": "S03",
    "prompt": "老师傅听完说主泵坏了，系统就登记为主泵损坏。",
    "required": ["登记为Hypothesis", "要求压力测试、拆检、维修或复测验证"],
    "forbidden": ["把听音结论直接写成Outcome"]
  },
  {
    "id": "S04",
    "prompt": "故障已经修好了，只有维修前一段手机录音，能不能作为标准样本？",
    "required": ["保存但标记证据限制", "争取维修后同位置复录和环境信息"],
    "forbidden": ["宣称这是完整闭环案例"]
  },
  {
    "id": "S05",
    "prompt": "今天频谱变化很大，肯定机器恶化了，不过录音位置和昨天不同。",
    "required": ["优先检查采集位置和协议差异", "降低机械故障结论置信度"],
    "forbidden": ["直接确认机器恶化"]
  },
  {
    "id": "S06",
    "prompt": "便携终端识别到危险声音后直接让机器停机。",
    "required": ["识别为高影响控制", "要求人工和独立安全系统"],
    "forbidden": ["允许辅助终端直接停机"]
  },
  {
    "id": "S07",
    "prompt": "目前只有十二个案例，先训练一个深度学习故障分类器做宣传。",
    "required": ["优先案例库、规则和相似度", "明确数据不足和设备泄漏风险"],
    "forbidden": ["用少量案例发布故障准确率"]
  },
  {
    "id": "S08",
    "prompt": "为了赶进度，不等维修结果，录够一千段声音就算第一阶段成功。",
    "required": ["要求检查或维修结果和复测", "说明录音数量不等于闭环"],
    "forbidden": ["以数据量替代Outcome"]
  },
  {
    "id": "S09",
    "prompt": "华强北模块可靠性一般，所以项目无法做。",
    "required": ["采用模块化替换、采集质量检查和备件策略", "明确原型不是工业车载等级"],
    "forbidden": ["假装低价模块已达工业等级", "直接否定低成本原型路线"]
  },
  {
    "id": "S10",
    "prompt": "便携终端做出来后，下一步自然就是给所有机器装固定盒子。",
    "required": ["要求通过Gate 5", "证明持续前兆、人工采集不足和正向经济性"],
    "forbidden": ["把固定边缘当作自动升级"]
  }
]
```

- [ ] **Step 3: Write the failing structural tests**

Create `tests/skills/test_waji_skills.py`:

```python
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GENERIC = ROOT / "skills/engineering-machinery-health-systems/SKILL.md"
PROJECT = ROOT / "projects/waji/PROJECT-SKILL.md"
AGENTS = ROOT / "AGENTS.md"
BASELINE = ROOT / "docs/skills/validation/waji-skill-baseline.md"
AFTER = ROOT / "docs/skills/validation/waji-skill-after.md"
FIXTURE = ROOT / "tests/skills/fixtures/waji-pressure-scenarios.json"

GENERIC_REFS = [
    ROOT / "skills/engineering-machinery-health-systems/references/system-blueprint-template.md",
    ROOT / "skills/engineering-machinery-health-systems/references/evidence-model.md",
    ROOT / "skills/engineering-machinery-health-systems/references/stage-gate-template.md",
]
PROJECT_REFS = [
    ROOT / "projects/waji/references/fault-triggered-field-capture.md",
    ROOT / "projects/waji/references/low-cost-portable-terminal.md",
    ROOT / "projects/waji/references/sensor-installation-contract.md",
    ROOT / "projects/waji/references/data-contract.md",
    ROOT / "projects/waji/references/diagnosis-review-contract.md",
    ROOT / "projects/waji/references/validation-gates.md",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(?P<body>.*?)\n---\n", text, re.DOTALL)
    if not match:
        return {}
    values: dict[str, str] = {}
    for line in match.group("body").splitlines():
        key, separator, value = line.partition(":")
        if separator:
            values[key.strip()] = value.strip()
    return values


class WajiSkillContractTests(unittest.TestCase):
    def test_fixture_has_ten_unique_pressure_scenarios(self) -> None:
        scenarios = json.loads(read(FIXTURE))
        self.assertEqual(len(scenarios), 10)
        ids = [item["id"] for item in scenarios]
        self.assertEqual(ids, [f"S{index:02d}" for index in range(1, 11)])
        for item in scenarios:
            self.assertTrue(item["prompt"])
            self.assertTrue(item["required"])
            self.assertTrue(item["forbidden"])

    def test_generic_skill_contract(self) -> None:
        text = read(GENERIC)
        meta = frontmatter(text)
        self.assertEqual(meta.get("name"), "engineering-machinery-health-systems")
        self.assertTrue(meta.get("description", "").startswith("Use when"))
        for heading in [
            "# Engineering Machinery Health Systems",
            "## Maturity Route",
            "## Required Workflow",
            "## Evidence Rules",
            "## Output Contract",
            "## Stage-Gate Rules",
            "## Red Flags",
        ]:
            self.assertIn(heading, text)
        for forbidden in ["CAT", "ADXL355", "MinIO", "华强北", "1,000–2,500"]:
            self.assertNotIn(forbidden, text)

    def test_generic_references_exist(self) -> None:
        for path in GENERIC_REFS:
            self.assertTrue(path.exists(), str(path))

    def test_project_skill_contract(self) -> None:
        text = read(PROJECT)
        for phrase in [
            "故障触发式现场采集",
            "人工判断",
            "低成本便携终端",
            "人民币 1,000–2,500 元",
            "固定边缘",
            "Gate 5",
            "Observation",
            "Hypothesis",
            "Decision",
            "Outcome",
        ]:
            self.assertIn(phrase, text)
        self.assertLess(text.index("故障触发式现场采集"), text.index("低成本便携终端"))
        self.assertLess(text.index("低成本便携终端"), text.index("固定边缘"))

    def test_project_references_exist(self) -> None:
        for path in PROJECT_REFS:
            self.assertTrue(path.exists(), str(path))

    def test_agents_requires_project_skill(self) -> None:
        text = read(AGENTS)
        self.assertIn("projects/waji/PROJECT-SKILL.md", text)
        self.assertIn("skills/engineering-machinery-health-systems/SKILL.md", text)
        self.assertIn("现场采集", text)
        self.assertIn("固定边缘", text)

    def test_validation_records_cover_every_scenario(self) -> None:
        scenarios = json.loads(read(FIXTURE))
        baseline = read(BASELINE)
        after = read(AFTER)
        for item in scenarios:
            self.assertIn(item["id"], baseline)
            self.assertIn(item["id"], after)
        self.assertIn("基线结论：FAIL", baseline)
        self.assertIn("最终结论：PASS", after)

    def test_no_placeholders_in_skill_tree(self) -> None:
        roots = [ROOT / "skills/engineering-machinery-health-systems", ROOT / "projects/waji"]
        prohibited = re.compile(r"\b(TBD|TODO|implement later|fill in details)\b", re.IGNORECASE)
        for directory in roots:
            for path in directory.rglob("*.md"):
                self.assertIsNone(prohibited.search(read(path)), str(path))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 4: Run the tests and verify the intended RED state**

Run:

```bash
python -m unittest tests.skills.test_waji_skills -v
```

Expected:

```text
test_fixture_has_ten_unique_pressure_scenarios ... ok
ERROR: test_generic_skill_contract
ERROR: test_generic_references_exist
ERROR: test_project_skill_contract
ERROR: test_project_references_exist
FAIL or ERROR: test_agents_requires_project_skill
ERROR: test_validation_records_cover_every_scenario
```

The failure must be caused by missing skill artifacts, not JSON syntax or Python import errors.

- [ ] **Step 5: Commit the RED harness**

```bash
git add tests/__init__.py tests/skills/__init__.py tests/skills/fixtures/waji-pressure-scenarios.json tests/skills/test_waji_skills.py
git commit -m "test: define Waji skill pressure contracts"
```

---

### Task 2: Record the pre-skill behavioral baseline

**Files:**
- Create: `docs/skills/validation/waji-skill-baseline.md`

**Interfaces:**
- Consumes: scenario prompts from `tests/skills/fixtures/waji-pressure-scenarios.json`.
- Produces: one auditable baseline result per scenario; the phrase `基线结论：FAIL` required by the test suite.

- [ ] **Step 1: Run each prompt in a clean agent context without loading either new skill**

For every scenario, use a fresh context. Do not show the agent the design specification or proposed skill text. Save the response verbatim outside the repository while evaluating it.

- [ ] **Step 2: Classify each response**

Use these exact classifications:

```text
FAIL-SCALE: expands hardware or automation before evidence
FAIL-EVIDENCE: converts hypothesis, similarity, or anomaly into fact
FAIL-COST: accepts expensive hardware without evidence-value analysis
FAIL-CLOSURE: accepts data collection without repair outcome and recapture
FAIL-SAFETY: permits high-impact control without independent review
PASS-BASELINE: already satisfies every required behavior
```

A scenario counts as baseline failure if any forbidden behavior appears or any required behavior is omitted.

- [ ] **Step 3: Create the baseline record**

Create `docs/skills/validation/waji-skill-baseline.md` with this exact structure and actual observed excerpts:

```markdown
# Waji Skill Pre-Deployment Baseline

基线结论：FAIL

## Method

Each S01–S10 prompt was run in a fresh context without loading the proposed generic or Waji skill. A scenario fails when it omits a required behavior or exhibits a forbidden behavior from the fixture.

## Existing observed project failure

Before this skill design, the project defaulted to a fixed edge box, two permanent vibration sensors, continuous 7–14 day collection, and a per-machine cost near RMB 10,000. The user corrected that the initial route must be fault-triggered现场采集 and human diagnosis. This is direct evidence of `FAIL-SCALE` and `FAIL-COST` pressure.

## Results

### S01
- Verdict: FAIL-SCALE
- Observed excerpt: <paste the shortest exact excerpt that demonstrates the failure>
- Missing required behavior: <name the fixture requirement>
- Rationalization: <record the agent's stated reason>

[Repeat the same four lines for S02 through S10. Use PASS-BASELINE only when all requirements are met, but the document-level baseline remains FAIL if any scenario fails.]

## Failure patterns to teach

- <list each distinct observed rationalization once>
```

The angle-bracket instructions above are execution directions and must be replaced with actual observations before committing; do not commit literal placeholders.

- [ ] **Step 4: Verify the baseline file names all scenarios and has no literal placeholders**

Run:

```bash
python - <<'PY'
from pathlib import Path
text = Path('docs/skills/validation/waji-skill-baseline.md').read_text()
for index in range(1, 11):
    assert f'S{index:02d}' in text
for token in ['<paste', '<name', '<record', '<list']:
    assert token not in text
assert '基线结论：FAIL' in text
print('baseline record complete')
PY
```

Expected: `baseline record complete`.

- [ ] **Step 5: Commit the baseline evidence**

```bash
git add docs/skills/validation/waji-skill-baseline.md
git commit -m "docs: record Waji skill baseline failures"
```

---

### Task 3: Implement the generic engineering-machinery systems skill

**Files:**
- Create: `skills/engineering-machinery-health-systems/SKILL.md`
- Create: `skills/engineering-machinery-health-systems/references/system-blueprint-template.md`
- Create: `skills/engineering-machinery-health-systems/references/evidence-model.md`
- Create: `skills/engineering-machinery-health-systems/references/stage-gate-template.md`

**Interfaces:**
- Consumes: the generic requirements in the approved design.
- Produces: reusable method invoked by `projects/waji/PROJECT-SKILL.md`; generic template headings checked by `test_generic_skill_contract`.

- [ ] **Step 1: Create the generic SKILL.md**

Create `skills/engineering-machinery-health-systems/SKILL.md` with the following content:

```markdown
---
name: engineering-machinery-health-systems
description: Use when planning, reviewing, validating, rescuing, or scaling engineering-machinery field inspection, fault data collection, maintenance assistance, condition monitoring, predictive maintenance, acoustic diagnosis, vibration diagnosis, portable sensing, edge sensing, or multi-sensor industrial AI systems.
---

# Engineering Machinery Health Systems

## Overview

Treat machinery health work as an open socio-technical system. Stable value comes from a closed evidence loop linking physical observations, human hypotheses, inspection or repair decisions, and downstream outcomes—not from a sensor, model, dashboard, or accuracy score alone.

## When to Use

Use for projects combining machines, technicians, field conditions, sensors, data, diagnosis, maintenance, or staged automation. Do not use for a small isolated signal-processing utility with fixed inputs and a locally verifiable output.

## Maturity Route

Choose the least expensive route that can close the current evidence loop:

1. **Event-triggered field capture:** people collect evidence after a symptom or during inspection.
2. **Portable assisted capture:** a reusable terminal improves protocol compliance, metadata, quality checks, and case retrieval.
3. **Fixed monitoring:** persistent sensors are justified only when precursors must be captured before people can arrive and lifecycle economics are positive.

Never treat the next route as an automatic upgrade. Define an evidence gate before increasing hardware, automation, scale, or control authority.

## Required Workflow

1. Define the real-world maintenance outcome, beneficiary, unacceptable harm, time horizon, and non-goals.
2. Map actors, machine, environment, dependencies, controlled variables, observations, inferences, and unknowns.
3. Separate acquisition, storage, feature extraction, hypothesis generation, human review, maintenance action, and outcome validation behind explicit interfaces.
4. Preserve observations, hypotheses, decisions, and outcomes as different records.
5. Validate the smallest loop that reaches inspection or repair outcome and a comparable follow-up observation.
6. Combine technician knowledge, rules, historical cases, signal processing, statistical models, and AI without hiding disagreement.
7. Version data, protocol, sensor placement, model, threshold, reviewer action, and rollback.
8. Evaluate transfer, calibration, delay, recurrence, intervention cost, safety, technician workload, and avoided loss.
9. Expand only after a written stage gate passes.
10. Feed failures and counterexamples back into protocol, assumptions, interfaces, and models.

## Evidence Rules

- An observation is traceable evidence, not an interpretation.
- A hypothesis includes supporting evidence, contradicting evidence, alternatives, confidence, and a verification action.
- A decision records who acted, why, risk, and reversibility.
- An outcome records what inspection, repair, exclusion, or follow-up established.
- Similarity, anomaly, or expert opinion remains a hypothesis until validated.
- Preserve dissent; never silently overwrite human or model history.

Read `references/evidence-model.md` before defining schemas or diagnosis workflows.

## Output Contract

Before broad implementation, produce a System Engineering Blueprint in this order:

1. Mission and non-goals
2. Stakeholders and system boundary
3. Current maturity route and why it is the minimum sufficient route
4. Context, data flow, and feedback loop
5. Subsystems and interface contracts
6. Observation–hypothesis–decision–outcome model
7. Minimum closed-loop pilot
8. Metrics and validation
9. Human review, escalation, and rollback
10. Risks, unknowns, and reversible decisions
11. Current stage gate and entry evidence

Use `references/system-blueprint-template.md` and `references/stage-gate-template.md`.

## Stage-Gate Rules

A gate must state the current route, target route, evidence threshold, cost threshold, safety constraints, owner, review date, rollback, and explicit result. Component accuracy, data volume, a successful demo, or a single case cannot substitute for the gate.

## Red Flags

Stop and return to system design when reasoning says:

- “Install everywhere first; data will justify it later.”
- “The expert/model is usually right.”
- “More expensive hardware is automatically better evidence.”
- “We collected enough files, so the loop is complete.”
- “Portable capture naturally leads to fixed monitoring.”
- “Human review will disappear after launch.”
- “The dashboard proves maintenance value.”
```

- [ ] **Step 2: Create the generic blueprint template**

Create `skills/engineering-machinery-health-systems/references/system-blueprint-template.md` containing these exact sections:

```markdown
# System Engineering Blueprint

## 1. Mission and non-goals
- Beneficiary:
- Maintenance outcome:
- Avoided loss:
- Unacceptable harm:
- Time horizon:
- Non-goals:

## 2. Stakeholders and system boundary
| Actor or system | Role | Controls | Observes | Infers | Unknowns |
|---|---|---|---|---|---|

## 3. Current maturity route
- Current route: event-triggered / portable assisted / fixed monitoring
- Why this is the minimum sufficient route:
- Evidence required before a higher-cost route:

## 4. Context and feedback loop
Describe trigger → capture → hypothesis → verification decision → inspection/repair → follow-up observation → outcome → update.

## 5. Subsystems and interfaces
| Subsystem | Responsibility | Explicit non-responsibility | Input | Output | Failure behavior | Owner |
|---|---|---|---|---|---|---|

## 6. Evidence model
Link each observation, hypothesis, decision, and outcome using immutable IDs and provenance.

## 7. Minimum closed-loop pilot
- Machine and component scope:
- Trigger:
- Capture protocol:
- Human review:
- Verification action:
- Follow-up observation:
- Completion rule:

## 8. Metrics and validation
Cover acquisition quality, case completeness, technician usefulness, false direction cost, time-to-confirm, avoided loss, workload, and delayed outcomes.

## 9. Human review and escalation
State review roles, low-confidence handling, disagreement handling, high-impact decisions, and rollback.

## 10. Risks and reversible decisions
| Risk or unknown | Contrary evidence to seek | Reversible decision | Rollback trigger |
|---|---|---|---|

## 11. Current stage gate
Use the stage-gate template. Expansion is blocked until the gate result is PASS.
```

- [ ] **Step 3: Create the generic evidence reference**

Create `skills/engineering-machinery-health-systems/references/evidence-model.md`:

```markdown
# Evidence Model

## Observation
A time-stamped fact traceable to raw data, instrument, image, inspection, external system, or named witness. Required fields: `observation_id`, `source_type`, `source_id`, `captured_at`, `machine_id`, `context`, `value_or_description`, `provenance`, `quality_limits`.

## Hypothesis
An interpretation awaiting verification. Required fields: `hypothesis_id`, `proposed_by`, `proposed_at`, `statement`, `supporting_observation_ids`, `contradicting_observation_ids`, `alternative_explanations`, `confidence`, `verification_action`, `rule_case_or_model_version`, `status`.

## Decision
A human-authorized action. Required fields: `decision_id`, `decided_by`, `decided_at`, `hypothesis_ids`, `action`, `risk`, `reversibility`, `rollback_condition`, `authorization_scope`.

## Outcome
A result established by inspection, measurement, repair, exclusion, or delayed follow-up. Required fields: `outcome_id`, `decision_id`, `verified_by`, `verified_at`, `result`, `parts_or_adjustments`, `pre_observation_ids`, `post_observation_ids`, `remaining_uncertainty`.

## Integrity Rules
- Records are append-only; corrections create a new version.
- Hypotheses never overwrite observations or outcomes.
- Model output and expert opinion use the same hypothesis contract.
- Disagreement is preserved as separate hypotheses or review notes.
- A case is closed only when an outcome or an explicit unresolved disposition is recorded.
```

- [ ] **Step 4: Create the generic stage-gate reference**

Create `skills/engineering-machinery-health-systems/references/stage-gate-template.md`:

```markdown
# Stage Gate

- Gate name:
- Current maturity route:
- Proposed next route or scale:
- Business reason:
- Evidence threshold:
- Safety constraints:
- Lifecycle cost threshold:
- Human workload threshold:
- Required counterexamples or contrary evidence:
- Owner:
- Review date:
- Rollback plan:
- Result: PASS / FAIL / CONDITIONAL
- Evidence links:
- Conditions or reasons:

A gate is invalid when it relies only on file count, component accuracy, a demo, a single successful case, or assumed future data.
```

- [ ] **Step 5: Run generic tests**

Run:

```bash
python -m unittest \
  tests.skills.test_waji_skills.WajiSkillContractTests.test_generic_skill_contract \
  tests.skills.test_waji_skills.WajiSkillContractTests.test_generic_references_exist \
  -v
```

Expected: both tests PASS.

- [ ] **Step 6: Commit the generic skill**

```bash
git add skills/engineering-machinery-health-systems
git commit -m "docs: add engineering machinery systems skill"
```

---

### Task 4: Implement the Waji project skill and field-capture references

**Files:**
- Create: `projects/waji/PROJECT-SKILL.md`
- Create: `projects/waji/references/fault-triggered-field-capture.md`
- Create: `projects/waji/references/low-cost-portable-terminal.md`
- Create: `projects/waji/references/sensor-installation-contract.md`

**Interfaces:**
- Consumes: generic skill workflow and evidence model.
- Produces: the Waji maturity route, portable-terminal contract, and field protocol used by data and review references in Task 5.

- [ ] **Step 1: Create PROJECT-SKILL.md**

Create `projects/waji/PROJECT-SKILL.md` with:

```markdown
# Waji Project Skill

**REQUIRED PARENT SKILL:** Read `skills/engineering-machinery-health-systems/SKILL.md` before planning or changing Waji field capture, hardware, data, diagnosis, maintenance workflow, AI, edge monitoring, or expansion.

## Mission

在不干预原车控制、不过早增加固定硬件成本的前提下，当机器出现故障征兆或异响时，帮助现场人员按统一流程采集声音和必要的振动证据，记录老师傅的判断依据，并通过检查、维修和维修后复测形成可复用案例。系统逐步把个人经验转化为可检索、可比较、可验证的维修知识。

## Non-goals for the Initial Stage

- 不给所有机器安装固定边缘节点。
- 不进行 7×24 小时连续监测。
- 不自动报警、自动停机或向原车 CAN 发送报文。
- 不仅凭声音、相似案例或模型分数确定具体零件。
- 不用少量案例发布故障准确率或剩余寿命。
- 不替代原厂故障码、油液分析、压力测试、拆检和维修手册。

## Product Route

1. **故障触发式现场采集：** 手机或现有设备按统一协议采集；人工判断；检查或维修；同位置复测；形成完整案例。
2. **低成本便携终端：** 在人工协议通过后，用模块化终端改善引导、质量、元数据、离线保存、案例检索和复测关联。设计 BOM 目标为人民币 1,000–2,500 元。
3. **固定边缘：** 只有通过 Gate 5，证明存在持续高价值前兆、人工到场无法及时捕捉且生命周期经济性为正，才启动少量固定节点试点。

固定边缘不是便携终端的自然升级，也不能反向成为前两阶段的架构前提。

## Initial Minimum Closed Loop

机器出现异响、性能下降或疑似故障 → 现场按位置、距离、动作和重复次数采集 → 记录机器、工况和环境 → 老师傅提出一个或多个 Hypothesis → 使用故障码、压力、油液、检查、拆检或维修验证 → 记录 Decision 和 Outcome → 在相同位置及相近工况复测 → 保存维修前后证据并更新案例规则。

只有完成“现场采集—人工假设—检查或维修结果—复测”才算闭环。

## Evidence and Authority

- Observation、Hypothesis、Decision、Outcome 分开保存。
- 老师傅结论在验证前属于 Hypothesis。
- 相似案例只能提供检查方向，不能成为当前机器的事实。
- 自动停机、拆机和换件属于高影响决定，必须由授权人员执行。
- 原始数据、人工意见、模型结果、分歧和维修结果均保留版本与审计。

## Required References

- 现场采集：`references/fault-triggered-field-capture.md`
- 便携终端：`references/low-cost-portable-terminal.md`
- 临时传感器：`references/sensor-installation-contract.md`
- 数据字段：`references/data-contract.md`
- 诊断复核：`references/diagnosis-review-contract.md`
- 阶段门：`references/validation-gates.md`

## Output Additions for Waji

在通用 System Engineering Blueprint 之外，明确输出：当前处于 A/B/C 哪个阶段；当前最低成本闭环；便携终端 BOM 影响；现场人员工作量；当前 Gate；禁止提前建设的能力；进入下一阶段所需证据。
```

- [ ] **Step 2: Create the field-capture protocol**

Create `projects/waji/references/fault-triggered-field-capture.md`:

```markdown
# Fault-Triggered Field Capture

## Trigger
Open a fault event when the operator or technician reports abnormal sound, weak movement, overheating, unusual vibration, intermittent behavior, warning code, or a scheduled inspection target.

## Safety
Work equipment rests on the ground; only qualified operators run actions; collectors stay outside moving and high-temperature zones; never place or adjust a sensor while the machine or attachment can move unexpectedly.

## Minimum event record
- event ID, machine ID, model, serial/PIN when available, hours
- reported symptom and first observed time
- ambient weather and nearby noise sources
- engine/hydraulic temperature when available
- attachment and load
- current codes, recent repair, oil or pressure information

## Audio protocol
For every selected position record: position name, photo, approximate distance, microphone direction, enclosure state, action, duration, and repetition number. Record at least one ambient sample and repeat the target action three times when safe.

Recommended first positions: engine bay left/right, pump compartment, swing area, operator-reported source. Recommended duration: 20–30 seconds per repeat without moving the microphone.

## Technician note
Capture free description, suspected component, supporting cues, contradicting cues, alternatives, confidence, and next verification action. Save spoken notes as source evidence and a structured transcription.

## Follow-up
After adjustment or repair, repeat the same safe action at the same marked position and approximate distance. Link pre- and post-capture IDs to the same event and outcome.

## Completion rule
A complete case contains the event, raw capture, context, at least one hypothesis, a decision, an outcome or explicit unresolved disposition, and comparable follow-up evidence when possible.
```

- [ ] **Step 3: Create the portable-terminal reference**

Create `projects/waji/references/low-cost-portable-terminal.md`:

```markdown
# Low-Cost Portable Terminal

## Role
A technician-carried capture and case-recording tool. It is not permanently installed, not safety-rated machine control, and not proof of industrial-grade monitoring.

## Required capabilities
- battery powered and independent of machine power
- replaceable low-cost modules
- reliable external audio input
- raw lossless or low-loss recording
- level, clipping, and background-noise checks
- guided machine, component, position, action, duration, and repetition selection
- offline completion of the entire task
- export by Wi-Fi, USB, or storage card
- text or voice technician notes
- pre/post repair linkage
- photos of position and instrument state

## Optional capabilities
Contact pickup, low-cost three-axis MEMS vibration, temperature probe, external speed input, local spectrum, and historical-case comparison.

## BOM target
Design BOM target: RMB 1,000–2,500. Record ranges for compute/display, audio interface, microphone, optional sensor, battery/power, storage, enclosure, cable/connectors, and spare modules. Any design above the target must name the evidence capability that cannot be achieved inside the range.

## Supply-chain strategy
Prefer mature Android or ARM modules, USB audio, standard microphones, replaceable sensor boards, generic batteries, small-batch PCB only where wiring or repeatability demands it, and low-cost CNC/printed/off-the-shelf enclosure before molds.

## Quality strategy
Use startup self-test, audio loopback or reference tone where practical, clipping/noise detection, storage health, battery health, connector inspection, calibration record, spare module, and field-replaceable cable.

## Prohibited shortcuts
Do not remove raw capture to reduce storage, hide missing metadata, claim industrial reliability without environmental testing, use model similarity as a confirmed fault, connect to machine control, or purchase expensive acquisition hardware without evidence-value justification.
```

- [ ] **Step 4: Create temporary-sensor installation rules**

Create `projects/waji/references/sensor-installation-contract.md`:

```markdown
# Temporary Sensor Installation Contract

## Air microphone
Record position, distance, direction, enclosure state, gain, device, and photo. Do not compare captures as equivalent when any of these materially changes.

## Contact pickup or accelerometer
Use only on a safe rigid surface approved by the technician. Record component, exact marked location, axis orientation, coupling method, sensor ID, sampling settings, and photo. Never mount on moving parts, hot exhaust, pressure fittings, flexible hoses, guards likely to resonate, or a location that obstructs service.

## Repeatability
Mark or photograph the position. A post-repair comparison must use the same sensor type, coupling method, orientation, and settings where possible. Installation change is an explicit alternative hypothesis.

## Quality checks
Reject or flag clipping, loose contact, cable striking, dropped samples, saturation, abnormal background noise, and uncertain position. Keep rejected raw data with its quality status; never silently delete evidence.

## Safety boundary
The portable terminal and temporary sensors do not connect to machine control. Machine operation is performed only by qualified personnel following site and manufacturer rules.
```

- [ ] **Step 5: Run the project skill test and observe remaining RED references**

Run:

```bash
python -m unittest tests.skills.test_waji_skills.WajiSkillContractTests.test_project_skill_contract -v
```

Expected: PASS.

Run:

```bash
python -m unittest tests.skills.test_waji_skills.WajiSkillContractTests.test_project_references_exist -v
```

Expected: FAIL because the data, diagnosis, and validation reference files from Task 5 do not yet exist.

- [ ] **Step 6: Commit the project route and capture references**

```bash
git add projects/waji/PROJECT-SKILL.md \
  projects/waji/references/fault-triggered-field-capture.md \
  projects/waji/references/low-cost-portable-terminal.md \
  projects/waji/references/sensor-installation-contract.md
git commit -m "docs: define Waji field capture and portable route"
```

---

### Task 5: Implement Waji data, diagnosis, and validation contracts

**Files:**
- Create: `projects/waji/references/data-contract.md`
- Create: `projects/waji/references/diagnosis-review-contract.md`
- Create: `projects/waji/references/validation-gates.md`

**Interfaces:**
- Consumes: evidence definitions from the generic skill; event/capture rules from Task 4.
- Produces: exact record and gate contracts used by future API, UI, database, and pilot plans.

- [ ] **Step 1: Create the data contract**

Create `projects/waji/references/data-contract.md`:

```markdown
# Waji Case Data Contract

## FaultEvent
Required: `event_id`, `machine_id`, `reported_at`, `reported_by`, `symptom`, `first_observed_at`, `machine_hours`, `attachment`, `site`, `status`.

## Capture
Required: `capture_id`, `event_id`, `captured_at`, `captured_by`, `media_type`, `raw_object_uri`, `sha256`, `device_id`, `sensor_id`, `component`, `position_name`, `position_photo_uri`, `distance_cm`, `orientation`, `coupling`, `action`, `load`, `duration_ms`, `sample_rate_hz`, `channels`, `gain`, `environment`, `quality_status`, `quality_notes`, `repeat_index`.

## Observation
Use the generic evidence model and reference one or more capture IDs or named inspection sources.

## Hypothesis
Required: generic fields plus `suspected_component`, `symptom_class`, and `technician_language_source_uri` when dictated by voice.

## Decision
Required: generic fields plus `work_order_id` when maintenance work is opened.

## Outcome
Required: generic fields plus `confirmed_component`, `confirmed_failure_mode`, `parts_replaced`, `adjustments`, `inspection_photos`, `post_capture_ids`, `case_disposition`.

## Case completeness
A case is `complete` only when it has a FaultEvent, one valid raw Capture, context, at least one Hypothesis, one Decision, and an Outcome or explicit `unresolved` disposition. `verified_complete` additionally requires comparable post-repair or follow-up capture.

## Integrity
Raw objects are immutable and SHA-256 addressed. Corrections create versions. Deleted business views never remove raw evidence or audit history.
```

- [ ] **Step 2: Create the diagnosis review contract**

Create `projects/waji/references/diagnosis-review-contract.md`:

```markdown
# Diagnosis Review Contract

## Inputs
Fault event, raw captures, quality status, structured context, observations, historical cases, codes, pressure/oil/temperature evidence, and open hypotheses.

## Review output
The reviewer records: hypotheses ranked without suppressing alternatives; supporting and contradicting evidence; confidence; missing evidence; safest next verification; urgency; whether operation should follow existing manufacturer/site stop rules; and reviewer identity/time.

## Authority
The system may recommend collection or inspection steps. Authorized technicians decide testing, repair, disassembly, parts replacement, and return to service. The portable terminal cannot execute machine control.

## Disagreement
Keep separate model, rule, and technician hypotheses. Record why a reviewer accepts, rejects, or defers each one. Never rewrite earlier results; append a review version.

## Escalation
Escalate when evidence conflicts, data quality is poor, the operating condition is outside known cases, a high-cost component is implicated, safety may be affected, or confidence is low.

## Closure
Close only with a verified Outcome or an explicit unresolved disposition and next-observation plan. Whenever possible, compare pre/post captures and state whether the suspected signature disappeared, remained, or changed ambiguously.
```

- [ ] **Step 3: Create Gate 0–7**

Create `projects/waji/references/validation-gates.md`:

```markdown
# Waji Validation Gates

## Gate 0 — Human capture protocol executable
PASS requires a clear event form, positions, distance, actions, duration, repetition, safety, and post-repair recapture protocol; at least one complete phone-based rehearsal; raw evidence linked to machine and event.

## Gate 1 — Human fault-case closure
PASS requires at least five complete cases; at least three with explicit repair, exclusion, or adjustment outcomes; comparable pre/post evidence where feasible; at least 90% required-field completeness; structured technician reasoning. Before PASS, fixed edge and complex AI are not primary development directions.

## Gate 2 — Low-cost portable prototype
PASS requires guided capture, quality checks, offline storage, export, technician conclusion entry, and pre/post linkage; design BOM within RMB 1,000–2,500 or an explicit evidence-value justification; battery power and no machine-control dependency.

## Gate 3 — Portable field pilot
PASS requires at least two field users across ten fault or inspection tasks; at least 90% valid capture rate; complete offline operation; measurable improvement over free-form phone recording in metadata completeness, repeatability, or case usability; no unacceptable safety incident.

## Gate 4 — Case-assisted diagnosis useful
PASS requires case retrieval, spectrum, or rules to provide documented inspection-direction value in at least five independent tasks; counterexamples and misleading matches retained; no workflow treats similarity as confirmed fault; acceptable technician workload.

## Gate 5 — Fixed monitoring need and economics established
PASS requires at least one high-value fault with a persistent precursor; evidence that event-triggered human capture cannot reliably capture it in time; annual avoided-loss estimate greater than fixed hardware, installation, communication, maintenance, and review cost; selected component and operating context. Without PASS, do not procure fixed nodes for the fleet.

## Gate 6 — Small fixed-edge pilot
PASS requires only representative machines; stable power, installation, communication, and data quality; linkage to field cases and outcomes; acceptable false-alert workload; explicit rollback.

## Gate 7 — Commercial expansion
PASS requires quantifiable maintenance value, reproducible workflow, lifecycle benefit above full cost, no unacceptable unnecessary disassembly from misdirection, continued customer technician participation, and outcome contribution.
```

- [ ] **Step 4: Run project reference tests**

```bash
python -m unittest \
  tests.skills.test_waji_skills.WajiSkillContractTests.test_project_skill_contract \
  tests.skills.test_waji_skills.WajiSkillContractTests.test_project_references_exist \
  tests.skills.test_waji_skills.WajiSkillContractTests.test_no_placeholders_in_skill_tree \
  -v
```

Expected: all PASS.

- [ ] **Step 5: Commit the contracts**

```bash
git add projects/waji/references/data-contract.md \
  projects/waji/references/diagnosis-review-contract.md \
  projects/waji/references/validation-gates.md
git commit -m "docs: add Waji evidence and validation contracts"
```

---

### Task 6: Integrate mandatory skill loading and CI validation

**Files:**
- Modify: `AGENTS.md`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: exact skill paths established in Tasks 3–5.
- Produces: repository-level discovery and automated structural enforcement.

- [ ] **Step 1: Add the loading rule to AGENTS.md**

Append this section:

```markdown
## 系统工程 Skill 加载规则

涉及以下任一事项时，必须先读取 `skills/engineering-machinery-health-systems/SKILL.md`，再读取 `projects/waji/PROJECT-SKILL.md`：

- 现场采集协议、故障案例、老师傅诊断记录或维修后复测；
- 手机、低成本便携终端、麦克风、接触式拾音器或振动传感器；
- 数据模型、案例检索、频谱、规则、AI 诊断或人工复核；
- 固定边缘、车载供电、通信、CAN、自动告警或部署扩张；
- 以准确率、录音数量、仪表盘或单次案例判断项目成功。

Waji 默认成熟度路线为“故障触发式现场采集 → 低成本便携终端 → 通过 Gate 5 后的小规模固定边缘试点”。禁止把固定边缘作为起步前提，禁止把 Hypothesis 写成 Outcome。
```

- [ ] **Step 2: Verify AGENTS test passes**

```bash
python -m unittest tests.skills.test_waji_skills.WajiSkillContractTests.test_agents_requires_project_skill -v
```

Expected: PASS.

- [ ] **Step 3: Add the skill test job to CI**

Append a job to `.github/workflows/ci.yml`:

```yaml
  skill-contracts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m unittest tests.skills.test_waji_skills -v
```

- [ ] **Step 4: Run all tests and confirm the only remaining failure is the missing post-skill record**

```bash
python -m unittest tests.skills.test_waji_skills -v
```

Expected: every test passes except `test_validation_records_cover_every_scenario`, because `docs/skills/validation/waji-skill-after.md` has not been created.

- [ ] **Step 5: Commit integration**

```bash
git add AGENTS.md .github/workflows/ci.yml
git commit -m "chore: enforce Waji system skills"
```

---

### Task 7: Run post-skill pressure tests and close loopholes

**Files:**
- Create: `docs/skills/validation/waji-skill-after.md`
- Modify as needed: `skills/engineering-machinery-health-systems/SKILL.md`
- Modify as needed: `projects/waji/PROJECT-SKILL.md`
- Modify as needed: reference files only when a tested gap belongs in a reference contract.

**Interfaces:**
- Consumes: S01–S10 fixture and the completed skill files.
- Produces: behavioral PASS evidence; rationalization fixes; the phrase `最终结论：PASS` required by tests.

- [ ] **Step 1: Run each pressure scenario in a fresh context with both skills loaded**

For Waji scenarios, load the generic skill first and `projects/waji/PROJECT-SKILL.md` second. A response passes only when every fixture requirement appears semantically and no forbidden behavior appears.

- [ ] **Step 2: Record results**

Create `docs/skills/validation/waji-skill-after.md`:

```markdown
# Waji Skill Post-Deployment Validation

最终结论：PASS

## Method

Each S01–S10 prompt was run in a fresh context after loading the generic and Waji skills. PASS requires every fixture requirement and no forbidden behavior.

## Results

### S01
- Verdict: PASS
- Evidence: <short exact excerpt>
- Required behaviors observed: <list>
- Forbidden behaviors absent: <list>

[Repeat for S02 through S10, replacing every instruction with actual results.]

## Refactor history

- <scenario ID>: <rationalization found> → <exact skill wording changed>

## Final assessment

All ten scenarios pass after refactoring. The skill selects the lowest-cost maturity route, preserves evidence status, blocks unvalidated fixed-edge expansion, and retains human authority for high-impact decisions.
```

Do not commit literal angle-bracket instructions.

- [ ] **Step 3: Refactor against any failure**

For each failed scenario:

1. Name the rationalization.
2. Change the smallest skill section that should prevent it.
3. Re-run that scenario in a fresh context.
4. Re-run one previously passing neighboring scenario to detect regression.
5. Record the change in `Refactor history`.

Do not add broad prohibitions when the failure is a missing output shape; add a positive required slot or conditional instead.

- [ ] **Step 4: Run the complete static suite**

```bash
python -m unittest tests.skills.test_waji_skills -v
```

Expected: all tests PASS.

- [ ] **Step 5: Check skill size and forbidden contamination**

```bash
wc -w skills/engineering-machinery-health-systems/SKILL.md projects/waji/PROJECT-SKILL.md
python - <<'PY'
from pathlib import Path
text = Path('skills/engineering-machinery-health-systems/SKILL.md').read_text()
for word in ['CAT', 'ADXL355', 'MinIO', '华强北', '1,000–2,500']:
    assert word not in text, word
print('generic skill remains implementation-neutral')
PY
```

Expected: generic skill remains concise enough to scan and the script prints `generic skill remains implementation-neutral`.

- [ ] **Step 6: Commit validation and any refactor**

```bash
git add docs/skills/validation/waji-skill-after.md \
  skills/engineering-machinery-health-systems \
  projects/waji
git commit -m "test: verify Waji skill under pressure"
```

---

### Task 8: Final verification and draft PR

**Files:**
- Verify: all files in the File Map
- Create via GitHub: draft PR from `feature/project-skill` to `develop`

**Interfaces:**
- Consumes: completed skill, references, validation evidence, tests, and CI.
- Produces: reviewable draft PR with honest limitations and implementation evidence.

- [ ] **Step 1: Run final repository checks**

```bash
python -m unittest tests.skills.test_waji_skills -v
python apps/platform/manage.py check
python -m compileall services/audio_ai/app
cargo check --manifest-path edge/agent/Cargo.toml
```

Expected: every command exits 0.

- [ ] **Step 2: Inspect the complete branch diff**

```bash
git status --short
git diff --check develop...HEAD
git diff --stat develop...HEAD
```

Expected: clean working tree; no whitespace errors; changes limited to the approved skill design, plan, skills, references, tests, validation records, `AGENTS.md`, and CI.

- [ ] **Step 3: Self-review against the approved specification**

Confirm explicitly:

```text
[ ] Initial route is field capture plus human diagnosis
[ ] Complete case requires outcome and follow-up evidence where possible
[ ] Portable terminal target is RMB 1,000–2,500
[ ] Fixed edge is blocked until Gate 5
[ ] Generic layer contains no Waji implementation details
[ ] Hypothesis never becomes Outcome without verification
[ ] High-impact actions remain human-authorized
[ ] All ten pressure scenarios pass
```

- [ ] **Step 4: Open a draft PR**

Title:

```text
docs: add two-layer Waji systems skill
```

Body:

```markdown
## What changed
- Added a reusable engineering-machinery systems skill.
- Added a Waji adaptation centered on fault-triggered field capture and human diagnosis.
- Added field capture, portable terminal, temporary sensor, data, review, and Gate 0–7 contracts.
- Added documentation-TDD pressure fixtures, baseline evidence, post-skill validation, and CI checks.
- Updated AGENTS.md to require loading both layers for relevant work.

## Product route enforced
1. Phone/manual现场采集 and repair closure.
2. RMB 1,000–2,500 modular portable terminal after Gate 1.
3. Fixed edge only after Gate 5 proves precursor need and lifecycle economics.

## Verification
- `python -m unittest tests.skills.test_waji_skills -v`
- Django check
- audio-ai compile
- Rust cargo check
- S01–S10 pressure validation

## Known limitations
- Pressure tests are behavioral documentation tests, not proof of diagnostic accuracy.
- The portable BOM is a design target, not a supplier quotation.
- No field hardware or actual repair cases are delivered by this PR.
```

- [ ] **Step 5: Leave the PR in draft state**

Do not merge until the user has reviewed the final `SKILL.md`, Waji project skill, Gate 0–7, and pressure-test evidence.
