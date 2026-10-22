# Examples

## `make_music.py`

A known-good result for the [first-prompt lesson](../docs/03-first-prompt.md).
It's here so the tutorial can't dead-end: if your agent produced silence, a
zero-byte file, or a broken WAV, run this to find out whether the problem is the
agent's code or your machine.

```sh
python3 make_music.py              # writes ./music.wav
python3 make_music.py out.wav      # custom path
open music.wav
```

Requires Python 3.9+ and **nothing else** — `math`, `wave`, `struct`, `random`
are all standard library. No `pip install`, no network, no samples.

### What it does

- Builds a 16-step motif and a variation in A minor pentatonic, so it's hard to
  sound dissonant.
- Two voices: a plucked melody and a held bass, each a fundamental plus two
  quiet harmonics.
- Attack/release envelope per note to avoid clicks, exponential decay so notes
  sound plucked rather than organ-like.
- A short feedback delay for space, peak normalisation, and a fade-out.
- Writes 44.1 kHz, 16-bit, mono PCM.

Output is about 13.6 seconds and runs in under a second.

### Why it's written this way

Every choice is one a reader can verify by ear and by code. If you're using this
to learn, the interesting parts are the envelope (why notes click without one)
and normalisation (why the mix clips or sounds tiny without it).

### Don't copy this into your first session

Type the prompt and let the agent make its own choices. The value is in seeing
what it picks and how it verifies. This file is a reference, not the answer —
and a different implementation is a feature, not a bug.

There's no test suite here on purpose. The verification *is* the guide's point:

```sh
afinfo music.wav     # is the header valid?
```

If you want to extend it, good first exercises: change the scale, add a
percussive track with filtered noise, or make the tempo ramp over time.
