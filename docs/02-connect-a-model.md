# Step 2 — Connect a model

Goal: pick a model and send it one prompt successfully.

OpenCode is a **harness**, not a model. It supplies the tools — read a file,
write a file, run a command — and the model supplies the judgement about which
tool to use. Without a connected model, the UI opens but nothing can think.

This is the single most common place people get stuck, so don't rush it.

---

## 2.1 Pick how you'll pay

There are three common routes. Any is fine; the guides don't care which you
choose.

| Route | Good when |
| --- | --- |
| **Provider API key** (Anthropic, OpenAI, Google, etc.) | You want one provider's models and per-token billing |
| **A subscription you already have** | Some providers let OpenCode use an existing coding plan via OAuth |
| **OpenCode Console / Go** | You want one account for many models without managing keys |

If you're unsure, an API key from a provider you already trust is the least
surprising option. Usage is metered, so you can see exactly what a session
costs.

## 2.2 Connect it

Start OpenCode from your scratch directory:

```sh
cd ~/scratch
opencode
```

Then, inside the TUI:

```text
/connect
```

This lists the integrations available to your install. Select your provider,
then follow the prompt. Depending on the provider you'll get one of:

- **API key** — paste the key. It's saved, you won't paste it again.
- **OAuth** — a browser URL or a device code. Press `o` to open the URL, `c` to
  copy the code.
- **Provider command** — OpenCode runs the provider's own login tool.

**Check:** `/connect` reports the provider as connected.

### Prefer the command line?

Same thing, without the TUI:

```sh
opencode auth login
```

With no arguments it opens a picker. To skip straight to one provider:

```sh
opencode auth login anthropic
```

Some providers offer more than one method. Run without `--method` first to see
them; to force API-key entry:

```sh
opencode auth login anthropic --method key
```

API-key entry and OAuth methods that ask you to paste a code need an
interactive terminal. If you're scripting this, that's the wall you'll hit —
there is no fully non-interactive path for those method types.

You can repeat `/connect` (or `auth login`) to add a second account, then switch
between them. Useful when you have a work account and a personal one.

## 2.3 Choose a model

```text
/models
```

Pick one. For the first run, a mid-tier model is the right call: capable enough
to write a small script, cheap enough that a mistake costs pennies.

Shortcuts, once the UI feels familiar:

| Action | Keys |
| --- | --- |
| Choose a model | `Ctrl+X` then `M` |
| Cycle recent models | `F2` |
| Choose an agent | `Ctrl+X` then `A` |

**Check:** the model name is visible in the prompt footer.

## 2.4 Send one throwaway prompt

Before the real lesson, prove the connection works:

```text
In one sentence, what does the `wave` module in Python's standard library do?
```

This exercises the model without touching a single file. You should get a
sensible answer in a few seconds.

If you get an authentication error instead, the key didn't save or the account
is inactive — go back to 2.2.

---

## Where your credentials actually live

Not in `opencode.json`. Not in your dotfiles. Saved keys and OAuth tokens live
in OpenCode's local SQLite database:

```sh
opencode debug paths db
```

Normally that's `~/.local/share/opencode/opencode.db`, though `XDG_DATA_HOME`
and `OPENCODE_DB` can move it.

Three consequences worth internalising:

1. **Never put a key in a config file.** Config gets committed. The database
   does not.
2. **Don't try to manage this by hand.** Editing the database is how people
   corrupt their setup. Use `/connect` and the `auth` commands.
3. **`auth list` is your source of truth** about what's connected.

```sh
opencode auth list
opencode auth switch              # picker, if you have multiple
opencode auth logout anthropic    # remove one account
```

### Environment variables instead of saved accounts

If your team injects credentials from a secrets manager, you can skip saved
accounts:

```sh
opencode service set env ANTHROPIC_API_KEY sk-ant-...
opencode auth list                # shows type "environment"
opencode service unset env ANTHROPIC_API_KEY
```

Note that setting an environment variable on the shared background service
**restarts** it. The next OpenCode command brings it back with the new value. A
saved account takes precedence over an environment connection for the same
provider, which is a subtle way to spend an hour wondering why your new key
isn't being used.

Some cloud providers use their native credential chain instead of a key —
Bedrock via the AWS chain, Vertex via Application Default Credentials:

```sh
gcloud auth application-default login
GOOGLE_CLOUD_PROJECT=my-project opencode
```

---

## Cost and rate limits

Two things to know before you write a long prompt:

- **Input tokens dominate early sessions.** Every file the agent reads is billed
  as input. Pointing it at a huge file to answer a small question is the
  expensive version of the same question.
- **Long sessions get more expensive per turn.** Context accumulates. This is
  why `/new` between unrelated tasks is both a cost control and a quality
  control.

If you hit a rate limit, the error is usually explicit about it. Switching
models (`/models`) or waiting for the window to reset is the fix. It is not
usually a bug in your setup.

---

## If something went wrong

### `/connect` shows no providers

You're probably on an old CLI. Check `opencode --version` and update with
`brew upgrade`.

### "No model selected" when sending a prompt

`/connect` succeeded but you never ran `/models`. OpenCode doesn't pick one for
you on a fresh install.

### Auth succeeds in the browser but the CLI still says not authenticated

The browser finished but the code wasn't pasted back, or it expired. Start the
flow again; device codes are short-lived.

### It works in one terminal but not another

You likely have two installs (say, Homebrew and npm). `which -a opencode` shows
all of them. Remove the extra one rather than debugging the mismatch.

---

**Next:** [Your first prompt](03-first-prompt.md)
