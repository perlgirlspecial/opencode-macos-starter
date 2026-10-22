# Step 3 — Your first prompt

Goal: a `.wav` file on disk that you can play, produced by a program the agent
wrote.

This is the payoff. Everything before this was setup.

---

## 3.1 Make a disposable directory

```sh
mkdir -p ~/scratch/music
cd ~/scratch/music
```

An empty directory is the point. There is nothing here to break, so you can pay
attention to *how* the agent works instead of worrying about what it's editing.

## 3.2 Start OpenCode

```sh
opencode
```

Confirm the model is selected in the footer. If it isn't, `/models`.

## 3.3 Type this exactly

```text
Create a small piece of new music for me
```

Then press `Enter`.

That's it. Deliberately vague.

## 3.4 What happens next

Your output will differ in wording, but the shape of a good run looks like
this. Read it as it goes — the process is the lesson.

```text
> Create a small piece of new music for me

  The agent considers what "music" means here. It has no audio generator,
  so it decides to synthesize a WAV file with a short Python script.

  ● write  make_music.py
  ● shell  python3 make_music.py
  │      wrote music.wav - 13.6s, 44100Hz, 16-bit mono
  ● shell  afinfo music.wav
  │      File type ID: WAVE ... 1 ch, 44100 Hz, Int16

  Done. I wrote make_music.py, a small synthesizer using only Python's
  standard library, and ran it to produce music.wav (13.6s). Play it with:

      open music.wav
```

**The agent may ask you a question first** — key, tempo, mood, length. Answer in
one line, or say "your call" and let it decide. Both are valid; noticing that it
asked is the interesting part.

**The agent may write something other than Python.** JavaScript, a Go program, a
MIDI file instead of WAV. That's fine. What matters is that it produced an
artifact you can verify.

## 3.5 Verify it yourself

Do not take "done" as done. Three checks:

```sh
ls -lh music.wav
```

A real file, with a plausible size. A 13-second stereo WAV is roughly 2 MB; a
mono 16-bit file is about half that. **`0 bytes` means it failed** and the agent
told you it succeeded anyway.

```sh
afinfo music.wav
```

macOS's audio inspector. You want to see `WAVE`, a sample rate like `44100 Hz`,
and `Int16`. If this errors, the file has a broken header.

```sh
open music.wav
```

It plays in Music, QuickTime, or whatever owns `.wav`. **Put headphones on.**
Your coworkers do not want to hear your first synthesizer experiment.

**Check:** you heard something that isn't a click, a test tone, or silence.

## 3.6 Iterate

The first result is a starting point, not a deliverable. Send a follow-up in
the same session:

```text
Make it 30 seconds, add a bassline, and make the ending fade out.
```

Then again:

```text
The melody is fine but the bass is too loud. Bring it down.
```

This is the rhythm of real agent work: **small, specific, verifiable
instructions.** "Make it better" is not a prompt; it's a wish.

You can also ask it to explain a decision:

```text
Why did you pick that tempo?
```

Or ask about the conversation without polluting it — useful when you want a
quick answer that shouldn't become context:

```text
/btw what octave is the melody in?
```

## 3.7 If your agent produced silence or nothing

This is the most instructive failure, so don't skip past it. Diagnose in order:

1. **Did the file get created?** `ls -l music.wav`. If nothing exists, the agent
   never ran its script — ask it to run the script and show the output.
2. **Is the file zero bytes?** The script crashed. Ask for the traceback.
3. **Does `afinfo` reject it?** Broken WAV header. Ask the agent to verify the
   header itself before claiming success.
4. **Does it play but sound like nothing?** Often an amplitude bug — samples all
   near zero after normalisation. Ask it to print the peak sample value.

Then compare against the known-good reference in this repository:

```sh
python3 examples/make_music.py reference.wav
afinfo reference.wav
open reference.wav
```

If the reference plays and yours doesn't, the problem is in the agent's code,
not your Mac. That's useful — it turns a vague "it's broken" into a specific
report you can act on.

## 3.8 Close the session

Start fresh before your next task:

```text
/new
```

or `Ctrl+X` then `N`.

One task per session. Carrying a finished task's context into a new one is how
sessions get expensive and how agents start "remembering" constraints you no
longer want.

---

## What you actually just did

You didn't prompt an AI to make music. You asked an agent to write a program,
run the program, and check the result — and then you checked the result too.

That loop is the entire job:

```
your intent  →  agent writes code  →  code runs  →  output
                      ↑                              │
                      └──────── verify ──────────────┘
```

The musical part was incidental. Swap the prompt for "add rate limiting to this
handler" and nothing about the loop changes.

---

**Next:** [What just happened](04-what-just-happened.md)
