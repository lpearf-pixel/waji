from __future__ import annotations

import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from core.models import Capture, Decision, FaultEvent, Hypothesis, Machine, Observation, Outcome
from core.services.audio_processing import process_capture_audio
from core.tests.helpers import make_wav_bytes


class FieldWorkflowTests(TestCase):
    def setUp(self) -> None:
        self.media = tempfile.TemporaryDirectory()
        self.settings = override_settings(MEDIA_ROOT=self.media.name)
        self.settings.enable()
        self.user = get_user_model().objects.create_user(username="field", password="secret")
        self.client.force_login(self.user)

    def tearDown(self) -> None:
        self.settings.disable()
        self.media.cleanup()

    def create_machine_event(self) -> tuple[Machine, FaultEvent]:
        machine = Machine.objects.create(make="CAT", model="320", fleet_id="EX-01", hours=3200)
        event = FaultEvent.objects.create(
            machine=machine,
            trigger="abnormal_sound",
            symptom="抬大臂时主泵区域异响",
            location="一号作业面",
            reporter=self.user,
        )
        return machine, event

    def create_capture(self, event: FaultEvent, stage: str) -> Capture:
        return Capture.objects.create(
            event=event,
            stage=stage,
            raw_file=SimpleUploadedFile(
                f"{stage}.wav", make_wav_bytes(frequency_hz=440.0 if stage == "pre" else 450.0), content_type="audio/wav"
            ),
            original_filename=f"{stage}.wav",
            content_type="audio/wav",
            device_label="现场手机",
            component="主泵区域",
            position_text="泵壳右侧固定标记",
            distance_m="0.20",
            direction="麦克风朝向泵壳",
            enclosure_state="机罩开启",
            action="怠速抬大臂",
            load="空载",
            gain_mode="自动增益",
            repeat_index=1,
            quality_status="valid",
            operator=self.user,
        )

    def test_dashboard_requires_login(self) -> None:
        self.client.logout()
        response = self.client.get(reverse("field-dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_collector_can_create_machine_and_event(self) -> None:
        response = self.client.post(
            reverse("machine-create"),
            {"make": "CAT", "model": "320", "fleet_id": "EX-02", "serial_number": "SN-02", "hours": 1200, "active": True},
        )
        self.assertEqual(response.status_code, 302)
        machine = Machine.objects.get(fleet_id="EX-02")
        response = self.client.post(
            reverse("event-create"),
            {
                "machine": machine.pk,
                "trigger": "abnormal_sound",
                "symptom": "回转时异响",
                "location": "二号作业面",
                "recent_repair": "无",
                "attachment": "标准斗",
                "environment_notes": "有轻微风声",
                "work_order_id": "WO-001",
                "workflow_status": "open",
            },
        )
        self.assertEqual(response.status_code, 302)
        event = FaultEvent.objects.get(machine=machine)
        self.assertEqual(event.reporter, self.user)
        self.assertEqual(response.url, reverse("event-detail", kwargs={"public_id": event.public_id}))

    def test_collector_can_upload_pre_capture(self) -> None:
        _, event = self.create_machine_event()
        response = self.client.post(
            reverse("capture-create", kwargs={"public_id": event.public_id}),
            {
                "stage": "pre",
                "raw_file": SimpleUploadedFile("phone.wav", make_wav_bytes(), content_type="audio/wav"),
                "device_label": "iPhone系统录音机",
                "component": "主泵区域",
                "position_text": "泵壳右侧固定标记",
                "distance_m": "0.20",
                "direction": "朝向泵壳",
                "enclosure_state": "机罩开启",
                "action": "怠速抬大臂",
                "load": "空载",
                "displayed_rpm": 800,
                "gain_mode": "自动增益",
                "repeat_index": 1,
                "manual_noise_reasons": ["wind"],
            },
        )
        self.assertEqual(response.status_code, 302)
        capture = Capture.objects.get(event=event)
        self.assertEqual(capture.operator, self.user)
        self.assertTrue(capture.raw_sha256)
        self.assertEqual(capture.processing_status, "completed")

    def test_event_page_shows_incomplete_then_verified_complete(self) -> None:
        _, event = self.create_machine_event()
        response = self.client.get(reverse("event-detail", kwargs={"public_id": event.public_id}))
        self.assertContains(response, "不完整")
        pre = self.create_capture(event, "pre")
        Observation.objects.create(
            event=event,
            capture=pre,
            statement="动作时异响增强",
            author=self.user,
            provenance="现场听音",
            quality_status="valid",
        )
        Hypothesis.objects.create(
            event=event,
            suspected_component="主泵",
            suspected_failure_mode="吸油异常",
            proposer=self.user,
            supporting_evidence="动作时异响增强",
            contradicting_evidence="尚未测压力",
            alternatives="滤芯堵塞",
            confidence="medium",
            missing_evidence="压力数据",
            safest_next_verification="停机检查滤芯",
        )
        Decision.objects.create(
            event=event,
            decision="停机检查滤芯",
            decider=self.user,
            urgency="same_day",
            risk="防止继续恶化",
            authority_basis="维修负责人",
            reversibility="可恢复",
            rollback_action="恢复原件",
            status="approved",
        )
        Outcome.objects.create(
            event=event,
            established_by=self.user,
            disposition="repaired",
            confirmed_component="吸油滤芯",
            failure_mode="堵塞",
            inspection_evidence="拆检确认",
            parts="滤芯",
            adjustments="换件排气",
            before_after_comparison="异响降低",
            closure_status="closed",
        )
        self.create_capture(event, "post")
        response = self.client.get(reverse("event-detail", kwargs={"public_id": event.public_id}))
        self.assertContains(response, "验证完整")

    def test_raw_and_processed_audio_are_rendered_as_separate_players(self) -> None:
        _, event = self.create_machine_event()
        capture = self.create_capture(event, "pre")
        process_capture_audio(capture)
        capture.refresh_from_db()
        response = self.client.get(reverse("event-detail", kwargs={"public_id": event.public_id}))
        self.assertContains(response, capture.raw_file.url)
        self.assertContains(response, capture.processed_file.url)
        self.assertContains(response, "原始录音")
        self.assertContains(response, "轻度去噪试听副本")
