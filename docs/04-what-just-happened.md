# Step 4 — What just happened

Goal: a mental model accurate enough to predict what the agent will do next,
and to debug it when it does something you didn't expect.

If you only read one page in this repo, read this one.

---

## The model did not make music

This is the important part, and it's where most beginners form a wrong model
that takes months to unlearn.

The model is a text predictor. It has no audio engine, no instrument, no
rendering pipeline. What happened was:

1. You sent text.
2. The model replied with **a plan and some code** — a Python script.
3. OpenCode executed that script as a **tool call** (`shell: python3 make_music.py`).
4. The script's stdout came back to the model as text.
5. The model read it and reported success.

The music came from `math.sin`, `wave`, and your CPU. The model wrote the
recipe; your machine did the cooking.

**Why this matters:** when an agent "can't" do something, the real question is
almost always "can we express this as code that runs?" It couldn't generate
audio — but it could absolutely write a program that does. That reframing is the
skill.

## The loop

Every task is the same loop, at different scales:

```
  ┌─────────────────────────────────────────────┐
  │                                             │
  ▼                                             │
read ──► decide ──► edit ──► run ──► observe ───┘
                                   │
                                   └──► (done, or report failure)
```

Four tools do most of the work:

| Tool | What it does |
| --- | --- |
| `read` | Opens a file. This is how it learns your code. |
| `edit` / `write` | Changes files — `edit` patches, `write` replaces. |
| `glob` / `grep` | Finds files and symbols without reading everything. |
| `shell` | Runs a command. This is where the real power and real risk live. |

A long agent run is just this loop repeated. When something goes wrong, look at
which step failed: did it misread (bad input), decide wrong (bad reasoning,
often bad context), edit wrong (small diff, easy to catch), or fail to run
(environment)?

That last distinction saves time. An agent that writes correct code into a
project that doesn't build isn't a bad agent; it's a broken environment, and
more prompting won't fix it.

## Permissions: the part you must understand

OpenCode's default policy is permissive. Every agent starts with:

```jsonc
[
  { "action": "*", "resource": "*", "effect": "allow" },
  { "action": "read", "resource": "*.env", "effect": "ask" },
  { "action": "read", "resource": "*.env.*", "effect": "ask" },
  { "action": "read", "resource": "*.env.example", "effect": "allow" }
]
```

Read that carefully: **allow everything, except `.env` files, which prompt.**

That's a sensible default for a tool meant to be productive immediately, and it
is not a safe default for a repository you care about. `shell` runs with your
user's filesystem, process, and network authority — the same as typing the
command yourself. An agent that decides `git push --force` is the fix will do
it, because nothing stopped it.

You'll tighten this in [step 5](05-best-practices.md). For now, just hold the
fact: **the default is allow-all.**

Three approval outcomes when a rule says `ask`:

| Choice | Effect |
| --- | --- |
| Allow once | Approve this one request |
| Allow always | Approve, and save a project-scoped rule for similar requests |
| Reject | Deny this and every other pending request in the session |

"Allow always" is convenient and it's how permission sets quietly widen over
weeks. Review saved approvals occasionally; they're just config you can edit.

Rules are ordered and **the last match wins**, which is why specific exceptions
come after broad rules:

```jsonc
{
  "permissions": [
    { "action": "shell", "resource": "*", "effect": "ask" },
    { "action": "shell", "resource": "git status *", "effect": "allow" }
  ]
}
```

If no rule matches, the answer is `ask`. That's the safe direction.

## Agents are roles, not models

OpenCode ships several agents. The two you'll use constantly:

- **`build`** — edits files and runs commands. The default.
- **`plan`** — investigates and proposes, but **cannot edit your files** (it can
  only write under `~/.opencode/plan`). This is enforced by permissions, not by
  the model's good manners.

Also present: `general` (parallel work, can't ask you questions), `explore`
(read-only search), and internal ones (`title`, `summary`, `compaction`) that you
should leave alone.

Switch with `Ctrl+X` then `A`, or `Shift+Tab` to cycle.

**The most useful habit in this entire guide:** on anything non-trivial, ask
`plan` first. Read its plan. Argue with the plan. *Then* switch to `build`.
Planning is free; a wrong implementation is not.

## Sessions and context

A session is one conversation with its own accumulating context. Everything the
agent reads stays in that context and is re-sent on every turn.

- `Ctrl+X` then `N`, or `/new` — start fresh.
- `Ctrl+X` then `L`, or `/sessions` — go back to an old one.
- `/undo` (`Ctrl+X` then `U`) — revert the last message **and the work it caused**.
- `/redo` — put it back.

Undo is a real safety net, but only down to the last revert point. It is not a
substitute for committing before you start.

Context is a budget, not a free resource. A session that has read forty files is
slower, more expensive, and more likely to lose the thread than a fresh one. The
usual cause of "the agent got dumber" is a session that should have ended an
hour ago.

## How it's put together

OpenCode is a TUI client talking to a background **service** that owns sessions,
configuration, permissions, and tool execution.

```
┌───────────┐     ┌──────────────────────┐     ┌──────────┐
│  TUI      │────►│  OpenCode service    │────►│  model   │
│  client   │◄────│  sessions, tools,    │◄────│  (API)   │
└───────────┘     │  permissions, config │     └──────────┘
                  └──────────────────────┘
```

This explains a family of confusing symptoms:

- Two terminal windows share one service, so they share config and can interfere.
- Restarting the TUI doesn't necessarily restart the service.
- `opencode --standalone` runs a private service, which is how you test whether
  the shared one is the problem.

## Where things live

| Thing | Location |
| --- | --- |
| Global config | `~/.config/opencode/opencode.json(c)` |
| Project config | `opencode.json(c)` or `.opencode/opencode.json(c)` |
| Project instructions | `AGENTS.md` (nested files load as the agent explores) |
| CLI preferences (theme, keys) | `~/.config/opencode/cli.json` |
| Credentials | SQLite DB — `opencode debug paths db` |
| Logs | `~/.local/share/opencode/log/opencode.log` |

Config is JSON or JSONC. Include the schema so your editor helps you:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
}
```

## Three mental corrections to make now

1. **It's not autocomplete.** Autocomplete suggests the next token. This thing
   runs commands and reads the results. Treat it like a fast, tireless colleague
   with no memory of yesterday and no fear of `rm`.

2. **It doesn't know if it succeeded.** It knows what the output *said*. That's
   why it "completes" tasks that don't work. Verification is your job until you
   have taught it — explicitly — how to verify.

3. **You're still the engineer.** The agent writes; you're accountable. "The AI
   did it" is not a postmortem.

---

**Next:** [Best practices](05-best-practices.md)
