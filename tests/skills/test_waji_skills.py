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
