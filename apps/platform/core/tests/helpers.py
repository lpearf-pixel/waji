from __future__ import annotations

import io
import math
import random
import struct
import wave


def make_wav_bytes(
    *,
    duration_seconds: float = 1.0,
    sample_rate: int = 8000,
    frequency_hz: float = 440.0,
    amplitude: float = 0.3,
    noise_amplitude: float = 0.0,
) -> bytes:
    """Return deterministic mono 16-bit PCM WAV bytes."""
    frame_count = max(1, int(duration_seconds * sample_rate))
    random_source = random.Random(42)
    samples: list[int] = []
    for index in range(frame_count):
        tone = amplitude * math.sin(2.0 * math.pi * frequency_hz * index / sample_rate)
        noise = noise_amplitude * random_source.uniform(-1.0, 1.0)
        value = max(-1.0, min(1.0, tone + noise))
        samples.append(int(round(value * 32767.0)))
    return make_pcm_wav_bytes(samples, sample_rate=sample_rate)


def make_pcm_wav_bytes(samples: list[int], *, sample_rate: int = 8000) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"".join(struct.pack("<h", sample) for sample in samples))
    return buffer.getvalue()
