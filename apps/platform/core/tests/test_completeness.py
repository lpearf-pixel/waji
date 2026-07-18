from __future__ import annotations

import tempfile
from datetime import date

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from core.models import Capture, Decision, FaultEvent, Hypothesis, Machine, Outcome
from core.services.completeness import evaluate_event_completeness
from core.tests.helpers import make_wav_bytes


class EventCompletenessTests(TestCase):
    def setUp(self) -> None:
        self.media = tempfile.TemporaryDirectory()
        self.settings = override_settings(MEDIA_ROOT=self.media.name)
        self.settings.enable()
        self.user = get_user_model().objects.create_user(username="technician", password="secret")
        self.machine = Machine.objects.create(make="CAT", model="320", fleet_id="EX-01")
        self.event = FaultEvent.objects.create(
            machine=self.machine,
            trigger="abnormal_sound",
            symptom="主泵区域异响",
            location="一号作业面",
            reporter=self.user,
        )

    def tearDown(self) -> None:
        self.settings.disable()
        self.media.cleanup()

    def add_capture(self, stage: str = "pre", quality_status: str = "valid") -> Capture:
        return Capture.objects.create(
            event=self.event,
            stage=stage,
            raw_file=SimpleUploadedFile(
                f"{stage}.wav", make_wav_bytes(frequency_hz=440.0 if stage == "pre" else 450.0), content_type="audio/wav"
            ),
            original_filename=f"{stage}.wav",
            content_type="audio/wav",
            device_label="现场手机",
            component="主泵区域",
            position_text="泵壳右侧固定标记",
            action="怠速抬大臂",
            quality_status=quality_status,
            operator=self.user,
        )

    def add_hypothesis(self) -> Hypothesis:
        return Hypothesis.objects.create(
            event=self.event,
            suspected_component="主泵",
            suspected_failure_mode="气蚀或吸油异常",
            proposer=self.user,
            supporting_evidence="异响随动作增强",
            contradicting_evidence="暂无压力测试",
            alternatives="吸油滤芯堵塞",
            confidence="medium",
            missing_evidence="压力与油液检查",
            safest_next_verification="读取压力并检查吸油管路",
        )

    def add_decision(self) -> Decision:
        return Decision.objects.create(
            event=self.event,
            decision="停机后检查吸油滤芯和管路",
            decider=self.user,
            urgency="same_day",
            risk="避免继续带故障高负载运行",
            authority_basis="现场维修负责人授权",
            reversibility="检查可撤销，不涉及自动控制",
            rollback_action="恢复原装件并复核",
            status="approved",
        )

    def add_outcome(self) -> Outcome:
        return Outcome.objects.create(
            event=self.event,
            established_by=self.user,
            disposition="repaired",
            confirmed_component="吸油滤芯",
            failure_mode="滤芯堵塞",
            inspection_evidence="拆检发现滤芯污染，换件后异响下降",
            parts="吸油滤芯",
            adjustments="更换滤芯并排气",
            before_after_comparison="维修后同位置录音异响显著降低",
            closure_status="closed",
        )

    def test_new_event_is_incomplete(self) -> None:
        result = evaluate_event_completeness(self.event)
        self.assertEqual(result.status, "incomplete")
        self.assertIn("pre_capture", result.missing)
        self.assertIn("hypothesis", result.missing)

    def test_pre_capture_hypothesis_decision_and_outcome_is_complete(self) -> None:
        self.add_capture()
        self.add_hypothesis()
        self.add_decision()
        self.add_outcome()
        result = evaluate_event_completeness(self.event)
        self.assertEqual(result.status, "complete")
        self.assertEqual(result.missing, ("post_capture",))

    def test_valid_post_capture_makes_case_verified_complete(self) -> None:
        self.add_capture("pre")
        self.add_capture("post")
        self.add_hypothesis()
        self.add_decision()
        self.add_outcome()
        result = evaluate_event_completeness(self.event)
        self.assertEqual(result.status, "verified_complete")
        self.assertEqual(result.missing, ())

    def test_oral_hypothesis_without_outcome_stays_incomplete(self) -> None:
        self.add_capture()
        self.add_hypothesis()
        self.add_decision()
        result = evaluate_event_completeness(self.event)
        self.assertEqual(result.status, "incomplete")
        self.assertIn("outcome_or_unresolved", result.missing)

    def test_explicit_unresolved_disposition_can_complete_case(self) -> None:
        self.add_capture()
        self.add_hypothesis()
        self.add_decision()
        self.event.unresolved_reason = "现场无法停机拆检"
        self.event.unresolved_next_condition = "下次计划停机时检查"
        self.event.unresolved_owner = self.user
        self.event.unresolved_due_date = date.today()
        self.event.save()
        result = evaluate_event_completeness(self.event)
        self.assertEqual(result.status, "complete")
        self.assertEqual(result.missing, ("post_capture",))
