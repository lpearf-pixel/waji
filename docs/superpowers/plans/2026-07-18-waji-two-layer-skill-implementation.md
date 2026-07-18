# Waji Two-Layer Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and verify a reusable engineering-machinery systems skill plus a Waji adaptation that starts with fault-triggered field capture and human diagnosis, advances to a RMB 1,000–2,500 portable terminal, and allows fixed edge monitoring only after a need-and-economics gate.

**Architecture:** The generic layer defines mission, boundary, evidence status, minimum closed loop, human authority, reversible decisions, and stage-gate discipline without naming CAT, named hardware, or infrastructure. The Waji layer supplies the concrete three-stage route, field protocol, portable-terminal contract, case schema, diagnosis review, and Gate 0–7. Python standard-library tests enforce file structure, required language, separation between generic and project layers, and validation-record coverage.

**Tech Stack:** Markdown, YAML frontmatter, JSON fixtures, Python 3.12 `unittest`, GitHub Actions, repository `AGENTS.md`.

## Global Constraints

- Phase A is fault-triggered field capture with a phone or portable device.
- A complete initial case is capture → human hypothesis → inspection or repair outcome → comparable follow-up capture when feasible.
- A technician opinion remains `Hypothesis` until evidence establishes an `Outcome`.
- Phase B portable-terminal design BOM target is RMB 1,000–2,500.
- The portable terminal is battery powered and independent of machine power and control.
- Phase C fixed edge monitoring begins only after Gate 5 proves a persistent high-value precursor, insufficient manual capture, and positive lifecycle economics.
- Audio similarity, anomaly score, spectrum, or dashboard never equals confirmed damage.
- No skill authorizes CAN transmission, automatic shutdown, automatic disassembly, or automatic parts replacement.
- The generic layer must not contain CAT, ADXL355, MinIO, 华强北, named phones, named boards, or the Waji BOM target.
- The Waji layer preserves raw evidence, provenance, version, dissent, reviewer action, and rollback.
- Skill creation follows documentation TDD: record pre-skill failures, write the smallest guidance that addresses them, rerun pressure cases, and close loopholes.

---

## File Map

### Generic layer
- Create: `skills/engineering-machinery-health-systems/SKILL.md`
- Create: `skills/engineering-machinery-health-systems/references/system-blueprint-template.md`
- Create: `skills/engineering-machinery-health-systems/references/evidence-model.md`
- Create: `skills/engineering-machinery-health-systems/references/stage-gate-template.md`

### Waji layer
- Create: `projects/waji/PROJECT-SKILL.md`
- Create: `projects/waji/references/fault-triggered-field-capture.md`
- Create: `projects/waji/references/low-cost-portable-terminal.md`
- Create: `projects/waji/references/sensor-installation-contract.md`
- Create: `projects/waji/references/data-contract.md`
- Create: `projects/waji/references/diagnosis-review-contract.md`
- Create: `projects/waji/references/validation-gates.md`

### Validation and integration
- Create: `tests/__init__.py`
- Create: `tests/skills/__init__.py`
- Create: `tests/skills/fixtures/waji-pressure-scenarios.json`
- Create: `tests/skills/test_waji_skills.py`
- Create: `docs/skills/validation/waji-skill-baseline.md`
- Create: `docs/skills/validation/waji-skill-after.md`
- Modify: `AGENTS.md`
- Modify: `.github/workflows/ci.yml`

---

### Task 1: Add failing contract tests and pressure fixtures

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/skills/__init__.py`
- Create: `tests/skills/fixtures/waji-pressure-scenarios.json`
- Create: `tests/skills/test_waji_skills.py`

**Interfaces:**
- Consumes: approved design specification.
- Produces: `python -m unittest tests.skills.test_waji_skills -v` and scenario IDs S01–S10.

- [ ] **Step 1: Create package markers**

Create empty files:

```text
tests/__init__.py
tests/skills/__init__.py
```

- [ ] **Step 2: Create the pressure fixture**

Create `tests/skills/fixtures/waji-pressure-scenarios.json`:

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

- [ ] **Step 3: Write the structural tests**

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

- [ ] **Step 4: Verify RED**

Run:

```bash
python -m unittest tests.skills.test_waji_skills -v
```

Expected: the fixture test passes; tests that read not-yet-created skill and validation files fail because those files are absent. Import and JSON parsing must succeed.

- [ ] **Step 5: Commit**

```bash
git add tests
git commit -m "test: define Waji skill pressure contracts"
```

---

### Task 2: Record the pre-skill baseline

**Files:**
- Create: `docs/skills/validation/waji-skill-baseline.md`

**Interfaces:**
- Consumes: S01–S10 prompts.
- Produces: an auditable record containing every scenario ID and `基线结论：FAIL`.

- [ ] **Step 1: Run S01–S10 without the new skills**

Use a fresh context for each prompt. Do not provide the new skill text or design. Save the exact response used for evaluation.

- [ ] **Step 2: Classify responses**

Use only these classifications:

```text
FAIL-SCALE
FAIL-EVIDENCE
FAIL-COST
FAIL-CLOSURE
FAIL-SAFETY
PASS-BASELINE
```

A scenario fails when one required behavior is absent or one forbidden behavior appears.

- [ ] **Step 3: Write the baseline record**

Create a Markdown document with:

- title `# Waji Skill Pre-Deployment Baseline`
- line `基线结论：FAIL`
- method explaining fresh contexts and fixture-based grading
- existing observed failure: the earlier project defaulted to permanent edge boxes, two vibration points, 7–14 day continuous collection, and roughly RMB 10,000 per machine before the user corrected the route
- sections `## S01` through `## S10`
- within every section: verdict, shortest exact excerpt proving the result, missing required behavior, forbidden behavior observed, and rationalization
- final section listing distinct failure patterns once

Every field must contain actual observed content. Do not commit an empty field, generic filler sentence, or instruction text.

- [ ] **Step 4: Validate the record**

```bash
python - <<'PY'
from pathlib import Path
text = Path('docs/skills/validation/waji-skill-baseline.md').read_text()
for index in range(1, 11):
    assert f'S{index:02d}' in text
assert '基线结论：FAIL' in text
assert 'Existing observed failure' in text or '现有已观察失败' in text
print('baseline record complete')
PY
```

Expected: `baseline record complete`.

- [ ] **Step 5: Commit**

```bash
git add docs/skills/validation/waji-skill-baseline.md
git commit -m "docs: record Waji skill baseline failures"
```

---

### Task 3: Add the generic systems skill

**Files:**
- Create: `skills/engineering-machinery-health-systems/SKILL.md`
- Create: `skills/engineering-machinery-health-systems/references/system-blueprint-template.md`
- Create: `skills/engineering-machinery-health-systems/references/evidence-model.md`
- Create: `skills/engineering-machinery-health-systems/references/stage-gate-template.md`

**Interfaces:**
- Consumes: baseline failure patterns.
- Produces: the parent method required by the Waji project layer.

- [ ] **Step 1: Create `SKILL.md`**

Use this exact content:

```markdown
---
name: engineering-machinery-health-systems
description: Use when planning, reviewing, validating, rescuing, or scaling engineering-machinery field inspection, fault data collection, maintenance assistance, condition monitoring, predictive maintenance, acoustic diagnosis, vibration diagnosis, portable sensing, edge sensing, or multi-sensor industrial AI systems.
---

# Engineering Machinery Health Systems

## Overview

Treat machinery health work as an open socio-technical system. Value comes from a closed evidence loop linking physical observations, human hypotheses, inspection or repair decisions, and downstream outcomes—not from a sensor, model, dashboard, or accuracy score alone.

## When to Use

Use for projects combining machines, technicians, field conditions, sensors, data, diagnosis, maintenance, or staged automation. Do not use for a small isolated signal-processing utility with fixed inputs and a locally verifiable output.

## Maturity Route

Choose the least expensive route that can close the current evidence loop:

1. **Event-triggered field capture:** people collect evidence after a symptom or during inspection.
2. **Portable assisted capture:** a reusable terminal improves protocol compliance, metadata, quality checks, and case retrieval.
3. **Fixed monitoring:** persistent sensors are justified only when precursors must be captured before people can arrive and lifecycle economics are positive.

Never treat the next route as an automatic upgrade. Define an evidence gate before increasing hardware, automation, scale, or control authority.

## Required Workflow

1. Define the maintenance outcome, beneficiary, unacceptable harm, time horizon, and non-goals.
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
- An outcome records what inspection, repair, exclusion, or delayed follow-up established.
- Similarity, anomaly, or expert opinion remains a hypothesis until validated.
- Preserve dissent; never silently overwrite human or model history.

Read `references/evidence-model.md` before defining schemas or diagnosis workflows.

## Output Contract

Before broad implementation, produce a System Engineering Blueprint in this order:

1. Mission and non-goals
2. Stakeholders and system boundary
3. Current maturity route and why it is minimum sufficient
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

A gate states the current route, target route, evidence threshold, cost threshold, safety constraints, owner, review date, rollback, and explicit result. Component accuracy, data volume, a successful demo, or a single case cannot substitute for the gate.

## Red Flags

Stop and return to system design when reasoning says:

- “Install everywhere first; data will justify it later.”
- “The expert or model is usually right.”
- “More expensive hardware is automatically better evidence.”
- “We collected enough files, so the loop is complete.”
- “Portable capture naturally leads to fixed monitoring.”
- “Human review will disappear after launch.”
- “The dashboard proves maintenance value.”
```

- [ ] **Step 2: Create generic references**

`system-blueprint-template.md` must contain eleven sections matching the Output Contract and tables for boundaries, subsystem interfaces, risks, and the current gate.

`evidence-model.md` must define required fields for Observation, Hypothesis, Decision, and Outcome, plus append-only integrity, versioning, dissent preservation, and case closure rules.

`stage-gate-template.md` must require: gate name, current route, proposed next route, business reason, evidence threshold, safety constraints, lifecycle cost threshold, workload threshold, contrary evidence, owner, review date, rollback, result, and evidence links.

Use the exact field names from the approved design. Do not introduce project-specific brands or costs.

- [ ] **Step 3: Run generic tests**

```bash
python -m unittest \
  tests.skills.test_waji_skills.WajiSkillContractTests.test_generic_skill_contract \
  tests.skills.test_waji_skills.WajiSkillContractTests.test_generic_references_exist \
  -v
```

Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add skills/engineering-machinery-health-systems
git commit -m "docs: add engineering machinery systems skill"
```

---

### Task 4: Add the Waji project skill and field-capture route

**Files:**
- Create: `projects/waji/PROJECT-SKILL.md`
- Create: `projects/waji/references/fault-triggered-field-capture.md`
- Create: `projects/waji/references/low-cost-portable-terminal.md`
- Create: `projects/waji/references/sensor-installation-contract.md`

**Interfaces:**
- Consumes: generic skill.
- Produces: Waji-specific route and field protocol.

- [ ] **Step 1: Create `PROJECT-SKILL.md`**

The file must include these exact requirements:

```text
REQUIRED PARENT SKILL: skills/engineering-machinery-health-systems/SKILL.md
Mission: fault-triggered现场采集, human diagnosis, inspection or repair, and comparable follow-up capture
Initial non-goals: fleet-wide fixed edge, continuous monitoring, automatic alarm or stop, CAN transmission, voice-only confirmed diagnosis, small-data accuracy marketing
Product route in order: 故障触发式现场采集 → 低成本便携终端 → 固定边缘
Portable BOM: 人民币 1,000–2,500 元
Fixed-edge condition: Gate 5
Evidence words: Observation, Hypothesis, Decision, Outcome
Authority: high-impact actions remain human-authorized
```

It must link all six Waji reference files and state that fixed edge is not a natural upgrade from the portable terminal.

- [ ] **Step 2: Create the field-capture protocol**

`fault-triggered-field-capture.md` must define:

- event triggers
- site safety and qualified-operator boundary
- event metadata
- microphone position, photo, distance, direction, enclosure state, gain, action, duration, repeat index
- ambient sample and three safe repetitions
- technician free description and structured hypothesis
- pre/post repair linkage
- complete-case rule

- [ ] **Step 3: Create the portable-terminal contract**

`low-cost-portable-terminal.md` must define:

- technician-carried role
- battery power and machine independence
- replaceable modules
- external audio, raw recording, clipping/noise checks, guided metadata, offline work, export, voice/text note, photo, pre/post link
- optional contact pickup, MEMS vibration, temperature, speed, spectrum, and case comparison
- RMB 1,000–2,500 BOM target
- mature module and small-batch supply strategy
- self-test, calibration, spare, and field-replacement strategy
- prohibited claims and shortcuts

- [ ] **Step 4: Create temporary-sensor rules**

`sensor-installation-contract.md` must define microphone repeatability, temporary contact or accelerometer placement, safe rigid surfaces, exact position/orientation/coupling records, rejected-quality states, and the rule that installation change is an alternative hypothesis.

- [ ] **Step 5: Run the project core test**

```bash
python -m unittest tests.skills.test_waji_skills.WajiSkillContractTests.test_project_skill_contract -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add projects/waji/PROJECT-SKILL.md projects/waji/references
git commit -m "docs: define Waji field capture and portable route"
```

---

### Task 5: Add Waji data, diagnosis, and Gate 0–7 contracts

**Files:**
- Create: `projects/waji/references/data-contract.md`
- Create: `projects/waji/references/diagnosis-review-contract.md`
- Create: `projects/waji/references/validation-gates.md`

**Interfaces:**
- Consumes: generic evidence model and Task 4 protocols.
- Produces: future API, database, UI, review, and pilot contracts.

- [ ] **Step 1: Create the data contract**

Define records and exact required field sets for:

```text
FaultEvent
Capture
Observation
Hypothesis
Decision
Outcome
```

Include machine, event, raw object URI, SHA-256, device, sensor, component, position photo, distance, orientation, coupling, action, load, duration, sample rate, gain, environment, quality, repeat index, suspected component, technician voice source, work order, confirmed component, failure mode, parts, adjustments, post captures, and disposition.

Define:

```text
complete = event + valid raw capture + context + hypothesis + decision + outcome or unresolved disposition
verified_complete = complete + comparable follow-up capture
```

Raw evidence is immutable and corrections create versions.

- [ ] **Step 2: Create the diagnosis review contract**

Require ranked hypotheses without hiding alternatives, support and contradiction, confidence, missing evidence, safest next verification, urgency, reviewer identity, human authority, disagreement preservation, escalation, and closure only by Outcome or explicit unresolved disposition.

- [ ] **Step 3: Create Gate 0–7**

Use these exact thresholds:

```text
Gate 0: one complete phone-based protocol rehearsal
Gate 1: five complete cases, three explicit outcomes, at least 90% required-field completeness
Gate 2: portable prototype, required features, BOM inside target or explicit evidence-value justification
Gate 3: two users, ten tasks, at least 90% valid capture, offline operation, measurable improvement over free-form phone recording
Gate 4: documented diagnostic-direction value in five independent tasks, counterexamples preserved
Gate 5: persistent high-value precursor, human capture insufficient, annual avoided loss exceeds full fixed-monitoring lifecycle cost
Gate 6: representative small fixed-edge pilot with stable power, installation, communication, data, linkage, workload, rollback
Gate 7: quantifiable value, reproducible workflow, lifecycle benefit above full cost, acceptable misdirection risk, continued technician participation
```

- [ ] **Step 4: Run Waji reference tests**

```bash
python -m unittest \
  tests.skills.test_waji_skills.WajiSkillContractTests.test_project_references_exist \
  tests.skills.test_waji_skills.WajiSkillContractTests.test_no_placeholders_in_skill_tree \
  -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add projects/waji/references
git commit -m "docs: add Waji evidence and validation contracts"
```

---

### Task 6: Integrate skill loading and CI

**Files:**
- Modify: `AGENTS.md`
- Modify: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: final skill paths.
- Produces: repository discovery and automated contract enforcement.

- [ ] **Step 1: Append the loading rule**

Append to `AGENTS.md`:

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

- [ ] **Step 2: Add CI job**

Append to `.github/workflows/ci.yml`:

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

- [ ] **Step 3: Run tests**

```bash
python -m unittest tests.skills.test_waji_skills -v
```

Expected: all structural tests pass except the post-skill validation-record test because `waji-skill-after.md` does not exist yet.

- [ ] **Step 4: Commit**

```bash
git add AGENTS.md .github/workflows/ci.yml
git commit -m "chore: enforce Waji system skills"
```

---

### Task 7: Run post-skill pressure tests and refactor

**Files:**
- Create: `docs/skills/validation/waji-skill-after.md`
- Modify when a tested loophole requires it: generic skill, Waji skill, or the reference that owns the missing contract.

**Interfaces:**
- Consumes: S01–S10 and both skill layers.
- Produces: `最终结论：PASS` and behavioral evidence for all ten scenarios.

- [ ] **Step 1: Run S01–S10 with both skills loaded**

Use a fresh context for each prompt. Load the generic skill first and Waji skill second. Pass requires every required behavior and no forbidden behavior.

- [ ] **Step 2: Write the post-skill record**

Create a Markdown document with:

- title `# Waji Skill Post-Deployment Validation`
- line `最终结论：PASS`
- method
- sections `## S01` through `## S10`
- within every section: verdict, shortest exact excerpt proving required behavior, required behaviors observed, forbidden behaviors confirmed absent
- refactor history naming each discovered rationalization and the exact wording changed
- final assessment

Every field must contain actual test evidence. Do not commit an empty field or instruction text.

- [ ] **Step 3: Close each loophole minimally**

For each failure:

1. name the rationalization
2. change the smallest owning section
3. rerun the failed scenario in a fresh context
4. rerun one neighboring previously passing scenario
5. record the change

Use positive output slots for missing-shape failures and explicit prohibitions only for deliberate discipline violations.

- [ ] **Step 4: Run complete test suite**

```bash
python -m unittest tests.skills.test_waji_skills -v
```

Expected: all PASS.

- [ ] **Step 5: Verify generic neutrality**

```bash
python - <<'PY'
from pathlib import Path
text = Path('skills/engineering-machinery-health-systems/SKILL.md').read_text()
for word in ['CAT', 'ADXL355', 'MinIO', '华强北', '1,000–2,500']:
    assert word not in text, word
print('generic skill remains implementation-neutral')
PY
```

Expected: `generic skill remains implementation-neutral`.

- [ ] **Step 6: Commit**

```bash
git add docs/skills/validation/waji-skill-after.md skills/engineering-machinery-health-systems projects/waji
git commit -m "test: verify Waji skill under pressure"
```

---

### Task 8: Final verification and draft PR

**Files:**
- Verify: all files in the File Map.
- Create through GitHub: draft PR from `feature/project-skill` to `develop`.

**Interfaces:**
- Consumes: completed skill, tests, validation records, and integration.
- Produces: reviewable draft PR.

- [ ] **Step 1: Run final checks**

```bash
python -m unittest tests.skills.test_waji_skills -v
python apps/platform/manage.py check
python -m compileall services/audio_ai/app
cargo check --manifest-path edge/agent/Cargo.toml
```

Expected: every command exits 0.

- [ ] **Step 2: Inspect branch scope**

```bash
git status --short
git diff --check develop...HEAD
git diff --stat develop...HEAD
```

Expected: clean working tree, no whitespace errors, and changes limited to design, plan, skills, references, tests, validation records, AGENTS, and CI.

- [ ] **Step 3: Review against specification**

Confirm all eight statements:

```text
Initial route is field capture plus human diagnosis.
Complete case includes outcome and follow-up evidence when feasible.
Portable terminal target is RMB 1,000–2,500.
Fixed edge is blocked until Gate 5.
Generic layer contains no Waji implementation details.
Hypothesis never becomes Outcome without verification.
High-impact actions remain human-authorized.
All ten pressure scenarios pass.
```

- [ ] **Step 4: Open a draft PR**

Title:

```text
docs: add two-layer Waji systems skill
```

PR body must state:

- reusable generic skill
- Waji field-first route
- six project references and Gate 0–7
- documentation-TDD baseline and post-skill evidence
- CI command
- BOM is a design target rather than supplier quotation
- no field hardware, repair cases, or diagnostic-accuracy claim is delivered by the PR

- [ ] **Step 5: Keep PR in draft**

Do not merge until the user reviews the final generic skill, Waji skill, Gate 0–7, and pressure-test evidence.
