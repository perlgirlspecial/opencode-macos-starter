# Step 6 — Troubleshooting

Work top to bottom. Most problems are one of four things: the binary isn't on
your `PATH`, no model is connected, the background service is unhealthy, or the
network/provider is refusing you.

Before anything else, note the two facts you'll need for any report:

```sh
opencode --version
sw_vers -productVersion && uname -m
```

---

## Triage

| Symptom | Likely cause | Jump to |
| --- | --- | --- |
| `opencode: command not found` | `PATH` or failed install | [Install](#command-not-found) |
| UI opens, no model in footer | Provider not connected, or no model chosen | [Auth](#no-model-connected) |
| "Authentication failed" | Expired key, wrong account, org policy | [Auth](#no-model-connected) |
| Hangs or is slow in every project | Shared service unhealthy | [Service](#the-service-is-stuck) |
| Wrote files but nothing ran | Permissions blocked `shell` | [Permissions](#a-command-was-blocked) |
| Works in one terminal, not another | Two installs | [Install](#two-installs) |
| `music.wav` is silent or 0 bytes | The script failed | [Music](#the-music-step-failed) |
| Random failures after an update | Version skew | [Updates](#after-an-update) |

---

## Install

### `command not found`

```sh
which -a opencode
ls /opt/homebrew/bin/opencode    # Apple silicon
ls /usr/local/bin/opencode       # Intel
```

If a file exists, it's a `PATH` problem — add Homebrew to your shell profile:

```sh
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
```

Then open a **new** terminal. `source`-ing works too, but a new window also
proves it survives a restart, which is the actual requirement.

If no file exists, the install didn't complete. Re-run it and read the output:

```sh
brew install anomalyco/tap/opencode-v2
```

### Two installs

`which -a opencode` listing two paths means you have, say, a Homebrew install
and an npm one. They update independently, so you run one and upgrade the other
— which looks like "the update did nothing".

Remove one. For an npm global:

```sh
npm uninstall -g @opencode/cli
```

### `Bad CPU type in executable`

Wrong architecture. `uname -m` says which you need (`arm64` = Apple silicon,
`x86_64` = Intel). Reinstall via Homebrew, which handles this for you.

### macOS blocks a downloaded binary

If you used the standalone zip rather than Homebrew, Gatekeeper may quarantine
it:

```sh
xattr -d com.apple.quarantine /path/to/opencode
```

Prefer Homebrew where you can — it avoids this whole class of problem.

## No model connected

```sh
opencode auth list
```

- **Empty list** → nothing connected. Run `/connect` in the TUI, or
  `opencode auth login`.
- **Provider listed but prompts fail** → the account may be inactive, out of
  quota, or blocked by an organisation policy. The error text usually names
  which.
- **Two accounts, wrong one active** → `opencode auth switch`.

In the TUI, confirm a model is actually selected in the footer. `/connect` adds
credentials; `/models` chooses what to use. They're separate steps and it's
normal to do one and not the other.

If you connected via an environment variable, remember it applies to the
**service**, not the terminal you're typing in:

```sh
opencode auth list     # look for type "environment"
opencode service set env ANTHROPIC_API_KEY sk-ant-...
```

Setting a service env var restarts the service. That's expected.

## The service is stuck

OpenCode's TUI talks to a background service. Most "it's hanging" bugs live
there, not in the model.

```sh
opencode service status
opencode service restart
opencode api get /api/info
```

`api get /api/info` is the honest health check: it uses the same discovery and
auth path as the TUI, and may start the service if none is running. If that
returns JSON but the TUI misbehaves, it's a client problem. If it fails, it's
the service.

### Isolate it

```sh
opencode --standalone
```

This runs the TUI with a **private** service. If standalone works and normal
mode doesn't, the shared service is the problem — restart it. If standalone also
fails, your install or config is the problem.

## A command was blocked

If files changed but nothing executed, a permission rule denied `shell`. The
TUI shows the rule when it blocks something.

Check your config for `deny` rules — remembering that the **last** matching rule
wins, so a stray broad `deny` after a narrow `allow` silently overrides it.
Saved "Allow always" approvals are project-scoped rules too, and can be edited.

## Logs

```sh
tail -f ~/.local/share/opencode/log/opencode.log
```

Filter by role to know which half is failing:

```sh
grep 'role=cli' ~/.local/share/opencode/log/opencode.log
grep 'role=server' ~/.local/share/opencode/log/opencode.log
```

- `role=cli` → startup and terminal client
- `role=server` → sessions, providers, plugins, permissions, tool execution

For one hard reproduction, turn the volume up:

```sh
OPENCODE_LOG_LEVEL=DEBUG opencode
```

Debug logs are noisy and may contain prompt text. Don't paste them wholesale
into a public issue.

## The music step failed

Check in this order:

```sh
ls -l music.wav        # exists? zero bytes?
afinfo music.wav       # valid WAV header?
open music.wav         # audible?
```

| Finding | Meaning | Next |
| --- | --- | --- |
| File missing | Script never ran | Ask the agent to run it and show output |
| 0 bytes | Script crashed before writing | Ask for the traceback |
| `afinfo` errors | Malformed header | Ask it to validate the header |
| Plays but silent | Amplitude/normalisation bug | Ask it to print peak sample value |

Then establish whether it's your Mac or the agent's code:

```sh
python3 examples/make_music.py reference.wav
afinfo reference.wav
open reference.wav
```

Reference plays, yours doesn't → the agent's code. Neither plays → your audio
output or Python install. That single comparison turns a vague bug report into a
specific one.

The reference script needs Python 3.9+ and **no packages**. If `python3 -V`
fails, run `xcode-select --install`.

## After an update

```sh
opencode --version
brew upgrade opencode-v2
```

If behaviour changed after an update, check `/highlights` — OpenCode shows
what's new once after a release, and it's easy to dismiss.

If a config fails to load after an update, suspect a V1-shaped field. V2 renamed
several: `permissions` (not `permission`), `shell` (not `bash`), `subagent` (not
`task`). The schema will flag unknown fields if your editor is wired to
`https://opencode.ai/config.json`.

## When you open an issue

Include:

- `opencode --version`, macOS version, `uname -m`
- the exact prompt and what you expected
- the error text, **redacted**
- whether `--standalone` changes anything
- relevant `role=cli` / `role=server` log lines

Never include API keys, auth headers, or private file contents. Redact first;
it's much harder to un-post something.

## What not to do

- **Don't delete or edit the SQLite database** to fix a problem. Back it up
  first if you must inspect it with external tools.
- **Don't `rm -rf` your config directory** as a first move. You'll lose saved
  accounts and approvals, and you won't learn what broke. Move it aside and
  restore it if the fresh config doesn't help.
- **Don't debug by installing a second copy.** That's how you get the two-install
  problem above.

---

**Back to:** [README](../README.md) · [Best practices](05-best-practices.md)
