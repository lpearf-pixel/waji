from __future__ import annotations

import math
import struct
import tempfile
import wave
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from core.models import Capture, FaultEvent, Machine
from core.services.audio_processing import inspect_wav, process_capture_audio
from core.tests.helpers import make_pcm_wav_bytes, make_wav_bytes


def dominant_frequency(path: Path, *, low_hz: int = 300, high_hz: int = 600) -> float:
    with wave.open(str(path), "rb") as wav_file:
        sample_rate = wav_file.getframerate()
        frame_count = min(wav_file.getnframes(), 4096)
        raw = wav_file.readframes(frame_count)
    samples = struct.unpack(f"<{frame_count}h", raw[: frame_count * 2])
    best_frequency = float(low_hz)
    best_power = -1.0
    bin_width = sample_rate / frame_count
    start_bin = max(1, int(low_hz / bin_width))
    end_bin = int(high_hz / bin_width) + 1
    for bin_index in range(start_bin, end_bin):
        frequency = bin_index * bin_width
        real = 0.0
        imaginary = 0.0
        for index, sample in enumerate(samples):
            angle = 2.0 * math.pi * bin_index * index / frame_count
            real += sample * math.cos(angle)
            imaginary -= sample * math.sin(angle)
        power = real * real + imaginary * imaginary
        if power > best_power:
            best_power = power
            best_frequency = frequency
    return best_frequency


class AudioProcessingTests(TestCase):
    def setUp(self) -> None:
        self.media = tempfile.TemporaryDirectory()
        self.settings = override_settings(MEDIA_ROOT=self.media.name)
        self.settings.enable()
        self.user = get_user_model().objects.create_user(username="audio", password="secret")
        self.machine = Machine.objects.create(make="CAT", model="320", fleet_id="EX-01")
        self.event = FaultEvent.objects.create(
            machine=self.machine,
            trigger="abnormal_sound",
            symptom="测试录音",
            location="试验区",
            reporter=self.user,
        )

    def tearDown(self) -> None:
        self.settings.disable()
        self.media.cleanup()

    def store_wav(self, payload: bytes | None = None) -> Capture:
        payload = payload or make_wav_bytes(duration_seconds=0.75, noise_amplitude=0.08)
        return Capture.objects.create(
            event=self.event,
            stage="pre",
            raw_file=SimpleUploadedFile("sample.wav", payload, content_type="audio/wav"),
            original_filename="sample.wav",
            content_type="audio/wav",
            device_label="现场手机",
            component="主泵",
            position_text="泵壳固定点",
            action="怠速动作",
            quality_status="review_required",
            operator=self.user,
        )

    def test_inspect_wav_reports_duration_rate_channels_and_valid_quality(self) -> None:
        capture = self.store_wav(make_wav_bytes(duration_seconds=1.0, sample_rate=8000, amplitude=0.25))
        inspection = inspect_wav(capture.raw_file.path)
        self.assertAlmostEqual(inspection.duration_seconds, 1.0, places=2)
        self.assertEqual(inspection.sample_rate, 8000)
        self.assertEqual(inspection.channels, 1)
        self.assertEqual(inspection.quality_status, "valid")
        self.assertGreater(inspection.rms, 0.1)

    def test_silence_is_invalid(self) -> None:
        capture = self.store_wav(make_wav_bytes(amplitude=0.0))
        inspection = inspect_wav(capture.raw_file.path)
        self.assertEqual(inspection.quality_status, "invalid_silence")
        self.assertIn("silence", inspection.quality_reasons)

    def test_clipped_audio_is_invalid(self) -> None:
        capture = self.store_wav(make_pcm_wav_bytes([32767] * 8000))
        inspection = inspect_wav(capture.raw_file.path)
        self.assertEqual(inspection.quality_status, "invalid_clipping")
        self.assertGreaterEqual(inspection.clipping_ratio, 0.01)

    def test_processing_creates_separate_derived_file_and_manifest(self) -> None:
        capture = self.store_wav()
        raw_name = capture.raw_file.name
        raw_hash = capture.raw_sha256
        processed = process_capture_audio(capture)
        processed.refresh_from_db()
        self.assertEqual(processed.raw_file.name, raw_name)
        self.assertEqual(processed.raw_sha256, raw_hash)
        self.assertTrue(processed.processed_file.name.endswith(".wav"))
        self.assertNotEqual(processed.processed_file.name, raw_name)
        self.assertEqual(processed.processing_status, "completed")
        self.assertEqual(processed.processing_manifest["input_sha256"], raw_hash)
        self.assertEqual(processed.processing_manifest["algorithm"], "waji-light-spectral-subtraction")
        self.assertEqual(processed.processing_manifest["output_sha256"], processed.processed_sha256)

    def test_light_denoise_preserves_dominant_frequency_within_one_fft_bin(self) -> None:
        capture = self.store_wav(
            make_wav_bytes(duration_seconds=1.0, sample_rate=8000, frequency_hz=440.0, amplitude=0.25, noise_amplitude=0.1)
        )
        process_capture_audio(capture)
        capture.refresh_from_db()
        detected = dominant_frequency(Path(capture.processed_file.path))
        bin_width = 8000 / 4096
        self.assertLessEqual(abs(detected - 440.0), bin_width)

    def test_unsupported_audio_keeps_raw_and_records_transparent_status(self) -> None:
        capture = Capture.objects.create(
            event=self.event,
            stage="pre",
            raw_file=SimpleUploadedFile("sample.m4a", b"not-a-real-m4a", content_type="audio/mp4"),
            original_filename="sample.m4a",
            content_type="audio/mp4",
            device_label="现场手机",
            component="主泵",
            position_text="泵壳固定点",
            action="怠速动作",
            quality_status="review_required",
            operator=self.user,
        )
        raw_hash = capture.raw_sha256
        with patch("core.services.audio_processing.shutil.which", return_value=None):
            process_capture_audio(capture)
        capture.refresh_from_db()
        self.assertEqual(capture.raw_sha256, raw_hash)
        self.assertFalse(bool(capture.processed_file))
        self.assertEqual(capture.processing_status, "raw_only_decode_unavailable")
        self.assertEqual(capture.processing_manifest["error"], "decoder_unavailable")
