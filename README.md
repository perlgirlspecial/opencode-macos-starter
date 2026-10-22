# Getting Started with OpenCode on a MacBook

A step-by-step starter for developers in their first few years — no AI tooling
experience assumed.

By the end you'll have OpenCode installed, connected to a model, and you'll have
made it write and run a real program that produces **a short piece of original
music**. You'll be able to play the file.

**Time:** about 20 minutes, most of it downloads.
**Cost:** a few cents on a pay-as-you-go API key. If you already pay for a
coding subscription, you may be able to use that instead.

---

## What this teaches

Installing a tool is the easy part and the least valuable part. Four things
here will still matter in a year:

1. **A setup you can reproduce.** Not "it worked once on my machine", but exact
   commands, in order, with a check after each one.
2. **How an agent actually produces an artifact.** The model does not generate
   audio. It writes a program, runs it, and reads the result. Once that clicks,
   every agent demo stops being magic.
3. **How to keep the blast radius small.** An agent runs with your user
   account's authority. Before you hand it a real repository, you need to know
   what it can touch.
4. **How to verify instead of trust.** You are the reviewer. Every time.

## Who this is for

You can use a terminal, you know what `git commit` does, and you've written
code in at least one language. You do not need to know anything about LLMs,
prompt engineering, or providers.

## What you need

| Requirement | Notes |
| --- | --- |
| macOS 13 or newer | Check with `sw_vers -productVersion` |
| Admin rights | Needed to install Homebrew and the Xcode command line tools |
| ~2 GB free disk | Homebrew, the CLI, and a model's dependencies |
| A model provider account | OpenCode does not include a model. See step 2. |

If you're on a corporate laptop with a locked-down MDM, some of these steps
will be blocked. That's normal and not your fault — talk to your platform team
before you try to work around it.

---

## The path

Work through these in order. Each one starts from a check that the previous one
finished.

| Step | Guide | You'll end up with |
| --- | --- | --- |
| 1 | [Set up your Mac](docs/01-setup-macos.md) | `opencode` on your `PATH` |
| 2 | [Connect a model](docs/02-connect-a-model.md) | A model you can send prompts to |
| 3 | [Your first prompt](docs/03-first-prompt.md) | `music.wav` that plays |
| 4 | [What just happened](docs/04-what-just-happened.md) | A mental model of the agent loop |
| 5 | [Best practices](docs/05-best-practices.md) | Habits for working in real repositories |
| 6 | [Troubleshooting](docs/06-troubleshooting.md) | A fix for when something breaks |

## The short version

If you already have Homebrew and a provider key, this is the whole thing:

```sh
brew install anomalyco/tap/opencode-v2
mkdir -p ~/scratch/music && cd ~/scratch/music
opencode
```

Then, inside OpenCode:

```text
/connect
/models
```

And once a model is selected:

```text
Create a small piece of new music for me
```

If that worked, still read [step 4](docs/04-what-just-happened.md) — that's
where the actual understanding is. If it didn't, start at
[step 1](docs/01-setup-macos.md).

---

## Why this first prompt

The classic first prompt is "build me a todo app". It's a bad first prompt. It
produces a hundred lines you won't read, in a directory you don't understand,
using a framework you didn't choose.

"Create a small piece of new music for me" is a better first task because:

- **It's safe.** It runs in an empty scratch directory. Nothing can be broken.
- **It's verifiable.** You can hear whether it worked. No judgement call about
  code quality.
- **It exercises the real loop.** Write a file, run a command, read the output,
  fix what's wrong. That's every agent task, just with a fun output.
- **It has a genuine failure mode.** Silent audio, a zero-byte file, a bad
  header. You'll get to practice verifying instead of assuming.

## House rules

Four rules, before you touch a real repository:

1. **Start in a scratch directory.** `~/scratch/` exists so that mistakes are
   free.
2. **Commit before you prompt.** If it's not committed, you can't tell what the
   agent changed.
3. **Read the diff.** Every line. It's your commit once you accept it.
4. **Deny what can't be undone.** Pushes, deploys, and `rm -rf` should require
   your explicit approval. Configuration is in
   [step 5](docs/05-best-practices.md).

---

## Repository layout

```text
.
├── README.md                  this file
├── docs/
│   ├── 01-setup-macos.md
│   ├── 02-connect-a-model.md
│   ├── 03-first-prompt.md
│   ├── 04-what-just-happened.md
│   ├── 05-best-practices.md
│   └── 06-troubleshooting.md
└── examples/
    ├── README.md
    └── make_music.py          known-good reference output
```

## A note on versions

OpenCode changes quickly. Commands here were checked against the V2 docs at
<https://opencode.ai/v2/docs/>. Version numbers are deliberately not pinned —
if a flag has changed, trust `opencode --help` and the official docs over this
guide, and please open an issue so the guide can be fixed.
