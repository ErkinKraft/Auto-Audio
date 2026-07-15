from __future__ import annotations

import io
import threading
import wave

import numpy as np


def _build_wav_bytes(duration: float = 0.85, sample_rate: int = 44100) -> bytes:
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    tone = (
        0.55 * np.sin(2 * np.pi * 440 * t)
        + 0.30 * np.sin(2 * np.pi * 660 * t)
        + 0.15 * np.sin(2 * np.pi * 880 * t)
    )
    envelope = np.ones_like(t)
    attack = int(0.04 * sample_rate)
    release = int(0.25 * sample_rate)
    envelope[:attack] = np.linspace(0, 1, attack)
    envelope[-release:] = np.linspace(1, 0, release)
    samples = (tone * envelope * 0.75 * 32767).astype(np.int16)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(samples.tobytes())
    return buf.getvalue()


_WAV_CACHE = _build_wav_bytes()


def play_preview(volume: float) -> None:
    """Play preview asynchronously. volume is 0.0–1.0."""
    volume = max(0.0, min(1.0, float(volume)))
    threading.Thread(target=_play_sync, args=(volume,), daemon=True).start()


def _play_sync(volume: float) -> None:
    try:
        import winsound

        raw = io.BytesIO(_WAV_CACHE)
        with wave.open(raw, "rb") as wf:
            params = wf.getparams()
            frames = wf.readframes(wf.getnframes())

        data = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
        data = (data * volume).astype(np.int16)

        out = io.BytesIO()
        with wave.open(out, "wb") as wf:
            wf.setparams(params)
            wf.writeframes(data.tobytes())

        winsound.PlaySound(out.getvalue(), winsound.SND_MEMORY)
    except Exception:

        try:
            import winsound

            winsound.Beep(880, 180)
            winsound.Beep(660, 220)
        except Exception:
            pass
