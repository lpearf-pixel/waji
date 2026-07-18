from __future__ import annotations

import hashlib
import tempfile

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from core.models import Capture, FaultEvent, Machine
from core.tests.helpers import make_wav_bytes


class CaptureIntegrityTests(TestCase):
    def setUp(self) -> None:
        self.media = tempfile.TemporaryDirectory()
        self.settings = override_settings(MEDIA_ROOT=self.media.name)
        self.settings.enable()
        self.user = get_user_model().objects.create_user(username="collector", password="secret")
        self.machine = Machine.objects.create(make="CAT", model="320", fleet_id="EX-01")
        self.event = FaultEvent.objects.create(
            machine=self.machine,
            trigger="abnormal_sound",
            symptom="液压动作时出现异响",
            location="一号作业面",
            reporter=self.user,
        )

    def tearDown(self) -> None:
        self.settings.disable()
        self.media.cleanup()

    def create_capture(self) -> Capture:
        payload = make_wav_bytes()
        return Capture.objects.create(
            event=self.event,
            stage="pre",
            raw_file=SimpleUploadedFile("pump.wav", payload, content_type="audio/wav"),
            original_filename="pump.wav",
            content_type="audio/wav",
            device_label="现场手机",
            component="主泵区域",
            position_text="主泵外壳右侧20厘米",
            action="怠速抬大臂",
            quality_status="valid",
            operator=self.user,
        )

    def test_initial_save_computes_raw_sha256(self) -> None:
        payload = make_wav_bytes()
        capture = Capture.objects.create(
            event=self.event,
            stage="pre",
            raw_file=SimpleUploadedFile("pump.wav", payload, content_type="audio/wav"),
            original_filename="pump.wav",
            content_type="audio/wav",
            device_label="现场手机",
            component="主泵区域",
            position_text="主泵外壳右侧20厘米",
            action="怠速抬大臂",
            quality_status="valid",
            operator=self.user,
        )
        self.assertEqual(capture.raw_sha256, hashlib.sha256(payload).hexdigest())

    def test_replacing_raw_file_raises_validation_error(self) -> None:
        capture = self.create_capture()
        capture.raw_file = SimpleUploadedFile(
            "replacement.wav", make_wav_bytes(frequency_hz=880.0), content_type="audio/wav"
        )
        with self.assertRaises(ValidationError):
            capture.save()

    def test_metadata_update_does_not_change_raw_sha256(self) -> None:
        capture = self.create_capture()
        original_hash = capture.raw_sha256
        original_name = capture.raw_file.name
        capture.action = "怠速收斗"
        capture.save()
        capture.refresh_from_db()
        self.assertEqual(capture.raw_sha256, original_hash)
        self.assertEqual(capture.raw_file.name, original_name)
