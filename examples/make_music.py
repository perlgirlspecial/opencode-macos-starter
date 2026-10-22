#!/usr/bin/env python3
"""Write a short original tune to music.wav using only the standard library.

This is the reference result for the "Create a small piece of new music for me"
lesson. It exists so the tutorial never dead-ends: if your agent's output is
silent or broken, run this to confirm your audio path works, then compare.

    python3 make_music.py            # writes ./music.wav
    python3 make_music.py out.wav    # custom path
    open music.wav                   # macOS: plays in the default app

No packages, no network, no samples. Just math and the wave module.
"""

from __future__ import annotations

import math
import random
import struct
import sys
import wave

SAMPLE_RATE = 44_100
CHANNELS = 1
SAMPLE_WIDTH = 2  # 16-bit PCM


def midi_to_hz(note: int) -> float:
    """MIDI note number -> frequency in Hz (A4 = 69 = 440Hz)."""
    return 440.0 * (2.0 ** ((note - 69) / 12.0))


def envelope(i: int, total: int, attack: float, release: float) -> float:
    """Simple attack/release envelope. Avoids clicks at note edges."""
    a = int(total * attack)
    r = int(total * release)
    if a > 0 and i < a:
        return i / a
    if r > 0 and i > total - r:
        return (total - i) / r
    return 1.0


def voice(freq: float, duration: float, amp: float, warmth: float = 0.35) -> list[float]:
    """One note: fundamental plus two quiet harmonics, with soft decay."""
    n = int(SAMPLE_RATE * duration)
    out = [0.0] * n
    for i in range(n):
        t = i / SAMPLE_RATE
        # A little detune keeps it from sounding like a pure test tone.
        w = 2.0 * math.pi * freq * t
        sample = (
            math.sin(w)
            + warmth * math.sin(2.0 * w)
            + warmth * 0.4 * math.sin(3.0 * w)
        )
        sample *= envelope(i, n, attack=0.02, release=0.35)
        # Exponential decay: plucked, not organ-like.
        sample *= math.exp(-2.5 * t / max(duration, 1e-6))
        out[i] = amp * sample
    return out


def add(target: list[float], source: list[float], offset: int) -> None:
    """Mix source into target at a sample offset, extending target if needed."""
    end = offset + len(source)
    if end > len(target):
        target.extend([0.0] * (end - len(target)))
    for i, s in enumerate(source):
        target[offset + i] += s


def echo(track: list[float], delay: float, feedback: float, mix: float) -> list[float]:
    """Cheap tape-style echo. Gives the loop a sense of space."""
    d = int(SAMPLE_RATE * delay)
    out = list(track)
    out.extend([0.0] * (d * 4))
    for i in range(d, len(out)):
        out[i] += out[i - d] * feedback * mix
    return out


def normalize(track: list[float], peak: float = 0.89) -> list[float]:
    high = max((abs(s) for s in track), default=0.0)
    if high == 0:
        return track
    gain = peak / high
    return [s * gain for s in track]


def write_wav(path: str, track: list[float]) -> None:
    with wave.open(path, "wb") as f:
        f.setnchannels(CHANNELS)
        f.setsampwidth(SAMPLE_WIDTH)
        f.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for s in track:
            # Clip then quantize to 16-bit signed range.
            clipped = max(-1.0, min(1.0, s))
            frames += struct.pack("<h", int(clipped * 32767))
        f.writeframes(bytes(frames))


def main() -> int:
    out_path = sys.argv[1] if len(sys.argv) > 1 else "music.wav"
    random.seed(2026)

    bpm = 84
    beat = 60.0 / bpm
    step = beat / 2  # eighth notes

    # A minor pentatonic, two octaves. Deliberately consonant: hard to make ugly.
    scale = [57, 60, 62, 64, 67, 69, 72, 74, 76, 79]

    # A 16-step motif, then a variation. Indices into `scale`.
    motif = [0, 2, 4, 2, 3, 4, 6, 4, 2, 0, 2, 4, 5, 4, 2, 0]
    variation = [0, 2, 4, 6, 7, 6, 4, 2, 4, 3, 2, 0, 2, 4, 2, 0]

    mix: list[float] = []

    # Melody: two passes with a slight human-ish timing drift.
    for pass_no, pattern in enumerate((motif, variation)):
        for i, idx in enumerate(pattern):
            note = scale[idx]
            dur = step * (1.6 if i % 4 == 0 else 0.95)
            drift = random.uniform(-0.006, 0.006)
            add(
                mix,
                voice(midi_to_hz(note), dur, amp=0.32),
                int((pass_no * 16 + i) * step * SAMPLE_RATE + drift * SAMPLE_RATE),
            )

    # Bass: root on the downbeat of each bar, held.
    bass_roots = [45, 45, 48, 43]  # A2, A2, C3, G2
    for bar, root in enumerate(bass_roots):
        for half in (0, 1):
            note = root if half == 0 else root + 7
            add(
                mix,
                voice(midi_to_hz(note), beat * 1.8, amp=0.20, warmth=0.15),
                int((bar * 4 + half * 2) * step * SAMPLE_RATE),
            )

    mix = echo(mix, delay=beat * 0.75, feedback=0.28, mix=0.35)
    mix = normalize(mix)

    # Short fade-out so the ending isn't a hard cut.
    fade = int(SAMPLE_RATE * 0.6)
    for i in range(min(fade, len(mix))):
        mix[len(mix) - 1 - i] *= i / fade

    write_wav(out_path, mix)
    seconds = len(mix) / SAMPLE_RATE
    print(f"wrote {out_path} — {seconds:.1f}s, {SAMPLE_RATE}Hz, 16-bit mono")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
