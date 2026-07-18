from __future__ import annotations

import hashlib
import io
import shutil
import subprocess
import tempfile
import wave
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from django.core.files.base import ContentFile
from django.utils import timezone

from core.models import Capture

ALGORITHM = "waji-light-spectral-subtraction"
ALGORITHM_VERSION = "1.0.0"
SUBTRACTION_FACTOR = 0.5
GAIN_FLOOR = 0.35
SILENCE_RMS = 0.001
CLIPPING_LEVEL = 0.995
INVALID_CLIPPING_RATIO = 0.01


class DecoderUnavailable(RuntimeError):
    pass


class DecodeFailed(RuntimeError):
    pass


@dataclass(frozen=True)
class AudioInspection:
    duration_seconds: float
    sample_rate: int
    channels: int
    peak: float
    rms: float
    clipping_ratio: float
    quality_status: str
    quality_reasons: tuple[str, ...]


def _read_pcm_wav(path: str | Path) -> tuple[np.ndarray, int]:
    try:
        with wave.open(str(path), "rb") as wav_file:
            if wav_file.getcomptype() != "NONE" or wav_file.getsampwidth() != 2:
                raise DecodeFailed("wav_must_be_uncompressed_16_bit_pcm")
            channels = wav_file.getnchannels()
            sample_rate = wav_file.getframerate()
            frame_count = wav_file.getnframes()
            raw = wav_file.readframes(frame_count)
    except (wave.Error, EOFError, OSError) as exc:
        raise DecodeFailed("invalid_wav") from exc
    values = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
    if channels < 1 or values.size == 0 or values.size % channels:
        raise DecodeFailed("invalid_pcm_shape")
    return values.reshape(-1, channels), sample_rate


def _inspection_from_samples(samples: np.ndarray, sample_rate: int) -> AudioInspection:
    channels = int(samples.shape[1])
    duration = float(samples.shape[0] / sample_rate)
    absolute = np.abs(samples)
    peak = float(np.max(absolute)) if samples.size else 0.0
    rms = float(np.sqrt(np.mean(np.square(samples)))) if samples.size else 0.0
    clipping_ratio = float(np.mean(absolute >= CLIPPING_LEVEL)) if samples.size else 0.0
    if rms < SILENCE_RMS:
        quality_status = Capture.QualityStatus.INVALID_SILENCE
        reasons = ("silence",)
    elif clipping_ratio >= INVALID_CLIPPING_RATIO:
        quality_status = Capture.QualityStatus.INVALID_CLIPPING
        reasons = ("clipping",)
    else:
        quality_status = Capture.QualityStatus.VALID
        reasons = ()
    return AudioInspection(
        duration_seconds=duration,
        sample_rate=sample_rate,
        channels=channels,
        peak=peak,
        rms=rms,
        clipping_ratio=clipping_ratio,
        quality_status=quality_status,
        quality_reasons=reasons,
    )


def inspect_wav(path: str | Path) -> AudioInspection:
    samples, sample_rate = _read_pcm_wav(path)
    return _inspection_from_samples(samples, sample_rate)


def _decode_with_ffmpeg(path: str | Path) -> tuple[np.ndarray, int]:
    executable = shutil.which("ffmpeg")
    if not executable:
        raise DecoderUnavailable("ffmpeg_not_found")
    with tempfile.TemporaryDirectory() as temporary_directory:
        output = Path(temporary_directory) / "decoded.wav"
        result = subprocess.run(
            [
                executable,
                "-nostdin",
                "-v",
                "error",
                "-y",
                "-i",
                str(path),
                "-vn",
                "-acodec",
                "pcm_s16le",
                str(output),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            check=False,
            timeout=120,
        )
        if result.returncode != 0 or not output.exists():
            raise DecodeFailed("ffmpeg_decode_failed")
        return _read_pcm_wav(output)


def _decode_capture(capture: Capture) -> tuple[np.ndarray, int, str]:
    try:
        source_path = Path(capture.raw_file.path)
    except (AttributeError, NotImplementedError) as exc:
        raise DecodeFailed("storage_path_unavailable") from exc
    if source_path.suffix.lower() == ".wav":
        try:
            samples, sample_rate = _read_pcm_wav(source_path)
            return samples, sample_rate, "wave"
        except DecodeFailed:
            pass
    samples, sample_rate = _decode_with_ffmpeg(source_path)
    return samples, sample_rate, "ffmpeg"


def _frame_matrix(signal: np.ndarray, frame_size: int, hop_size: int) -> tuple[np.ndarray, int]:
    original_length = signal.size
    if original_length < frame_size:
        signal = np.pad(signal, (0, frame_size - original_length))
    remainder = (signal.size - frame_size) % hop_size
    if remainder:
        signal = np.pad(signal, (0, hop_size - remainder))
    frame_count = 1 + (signal.size - frame_size) // hop_size
    frames = np.stack(
        [signal[index * hop_size : index * hop_size + frame_size] for index in range(frame_count)],
        axis=0,
    )
    return frames, original_length


def _noise_magnitude(
    frames: np.ndarray,
    window: np.ndarray,
    ambient_signal: np.ndarray | None,
    frame_size: int,
    hop_size: int,
) -> np.ndarray:
    if ambient_signal is not None and ambient_signal.size:
        ambient_frames, _ = _frame_matrix(ambient_signal, frame_size, hop_size)
        ambient_spectra = np.fft.rfft(ambient_frames * window, axis=1)
        return np.median(np.abs(ambient_spectra), axis=0)
    energies = np.mean(np.square(frames), axis=1)
    count = max(1, min(8, int(np.ceil(frames.shape[0] * 0.2))))
    indices = np.argsort(energies)[:count]
    spectra = np.fft.rfft(frames[indices] * window, axis=1)
    return np.median(np.abs(spectra), axis=0)


def _clean_channel(signal: np.ndarray, ambient_signal: np.ndarray | None = None) -> np.ndarray:
    signal = signal.astype(np.float64, copy=True)
    signal -= float(np.mean(signal))
    length = signal.size
    if length == 0:
        return signal
    maximum_frame = min(2048, max(256, 2 ** int(np.floor(np.log2(max(256, length))))))
    frame_size = int(maximum_frame)
    hop_size = max(1, frame_size // 4)
    frames, original_length = _frame_matrix(signal, frame_size, hop_size)
    window = np.hanning(frame_size)
    spectra = np.fft.rfft(frames * window, axis=1)
    magnitudes = np.abs(spectra)
    noise = _noise_magnitude(frames, window, ambient_signal, frame_size, hop_size)
    gain = 1.0 - SUBTRACTION_FACTOR * noise[np.newaxis, :] / (magnitudes + 1e-12)
    gain = np.clip(gain, GAIN_FLOOR, 1.0)
    cleaned_frames = np.fft.irfft(spectra * gain, n=frame_size, axis=1) * window
    output_length = (cleaned_frames.shape[0] - 1) * hop_size + frame_size
    output = np.zeros(output_length, dtype=np.float64)
    normalizer = np.zeros(output_length, dtype=np.float64)
    window_power = np.square(window)
    for index, frame in enumerate(cleaned_frames):
        start = index * hop_size
        output[start : start + frame_size] += frame
        normalizer[start : start + frame_size] += window_power
    valid = normalizer > 1e-10
    output[valid] /= normalizer[valid]
    return output[:original_length]


def _light_denoise(samples: np.ndarray, ambient_samples: np.ndarray | None = None) -> np.ndarray:
    cleaned = np.zeros_like(samples, dtype=np.float64)
    for channel in range(samples.shape[1]):
        ambient_channel = None
        if ambient_samples is not None and ambient_samples.shape[1] == samples.shape[1]:
            ambient_channel = ambient_samples[:, channel]
        cleaned[:, channel] = _clean_channel(samples[:, channel], ambient_channel)
    peak = float(np.max(np.abs(cleaned))) if cleaned.size else 0.0
    if peak > 0.98:
        cleaned *= 0.98 / peak
    return np.clip(cleaned, -1.0, 1.0)


def _wav_bytes(samples: np.ndarray, sample_rate: int) -> bytes:
    pcm = np.round(np.clip(samples, -1.0, 1.0) * 32767.0).astype("<i2")
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(int(samples.shape[1]))
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm.tobytes(order="C"))
    return buffer.getvalue()


def _failure_manifest(capture: Capture, *, error: str, status: str) -> Capture:
    manifest = {
        "algorithm": ALGORITHM,
        "version": ALGORITHM_VERSION,
        "input_sha256": capture.raw_sha256,
        "error": error,
        "created_at": timezone.now().isoformat(),
    }
    Capture.objects.filter(pk=capture.pk).update(
        processing_status=status,
        processing_manifest=manifest,
    )
    capture.refresh_from_db()
    return capture


def process_capture_audio(capture: Capture, *, ambient_capture: Capture | None = None) -> Capture:
    """Inspect and create a conservative derived listening copy without altering raw evidence."""
    try:
        samples, sample_rate, decoder = _decode_capture(capture)
    except DecoderUnavailable:
        return _failure_manifest(
            capture,
            error="decoder_unavailable",
            status="raw_only_decode_unavailable",
        )
    except (DecodeFailed, subprocess.TimeoutExpired, OSError):
        Capture.objects.filter(pk=capture.pk).update(quality_status=Capture.QualityStatus.INVALID_DECODE)
        return _failure_manifest(capture, error="decode_failed", status="raw_only_decode_failed")

    inspection = _inspection_from_samples(samples, sample_rate)
    quality_status = inspection.quality_status
    reasons = list(inspection.quality_reasons)
    for reason in capture.manual_noise_reasons or []:
        if reason not in reasons:
            reasons.append(reason)
    if quality_status == Capture.QualityStatus.VALID and reasons:
        quality_status = Capture.QualityStatus.USABLE_WITH_NOISE

    metadata = {
        "duration_seconds": inspection.duration_seconds,
        "sample_rate": inspection.sample_rate,
        "channels": inspection.channels,
        "quality_status": quality_status,
        "quality_reasons": reasons,
    }
    if quality_status in {
        Capture.QualityStatus.INVALID_CLIPPING,
        Capture.QualityStatus.INVALID_SILENCE,
        Capture.QualityStatus.INVALID_DECODE,
    }:
        Capture.objects.filter(pk=capture.pk).update(processing_status="quality_rejected", **metadata)
        capture.refresh_from_db()
        return capture

    ambient_samples = None
    ambient_id = None
    if ambient_capture is not None:
        try:
            candidate, ambient_rate, _ = _decode_capture(ambient_capture)
            if ambient_rate == sample_rate and candidate.shape[1] == samples.shape[1]:
                ambient_samples = candidate
                ambient_id = str(ambient_capture.public_id)
        except (DecoderUnavailable, DecodeFailed, subprocess.TimeoutExpired, OSError):
            ambient_samples = None

    cleaned = _light_denoise(samples, ambient_samples)
    output_bytes = _wav_bytes(cleaned, sample_rate)
    output_sha256 = hashlib.sha256(output_bytes).hexdigest()
    manifest = {
        "algorithm": ALGORITHM,
        "version": ALGORITHM_VERSION,
        "parameters": {
            "subtraction_factor": SUBTRACTION_FACTOR,
            "gain_floor": GAIN_FLOOR,
            "fft_size_max": 2048,
            "overlap": 0.75,
        },
        "input_sha256": capture.raw_sha256,
        "output_sha256": output_sha256,
        "ambient_capture_id": ambient_id,
        "decoder": decoder,
        "inspection": asdict(inspection),
        "created_at": timezone.now().isoformat(),
    }
    processed_field = Capture._meta.get_field("processed_file")
    generated_name = processed_field.generate_filename(capture, f"{capture.public_id}.wav")
    storage = processed_field.storage
    if storage.exists(generated_name):
        storage.delete(generated_name)
    saved_name = storage.save(generated_name, ContentFile(output_bytes))
    Capture.objects.filter(pk=capture.pk).update(
        processed_file=saved_name,
        processed_sha256=output_sha256,
        processing_status="completed",
        processing_manifest=manifest,
        **metadata,
    )
    capture.refresh_from_db()
    return capture
