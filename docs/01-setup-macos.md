# Step 1 — Set up your Mac

Goal: `opencode --version` prints a version number.

Every step ends with a check. Run it. Don't continue on a maybe.

---

## 1.1 Know what you're on

```sh
sw_vers -productVersion
uname -m
```

- `arm64` means Apple silicon (M1 and later).
- `x86_64` means Intel.

You need this if you ever download a standalone binary instead of using
Homebrew. Remember which one you are; mixing them produces confusing
`Bad CPU type in executable` errors later.

**Check:** you can say which macOS version and which architecture you have.

## 1.2 Open Terminal and make a scratch directory

Use the Terminal app (or iTerm2, or Ghostty — anything works).

```sh
mkdir -p ~/scratch
cd ~/scratch
pwd
```

The point of `~/scratch` is that it's disposable. Agents do their first,
messiest work here, never in `~/Documents/important-thing`.

**Check:** `pwd` prints `/Users/<you>/scratch`.

## 1.3 Install the Xcode command line tools

These provide `git`, `make`, and a usable `python3`. You probably have them
already.

```sh
xcode-select -p
```

If that prints a path like `/Library/Developer/CommandLineTools`, you're done.
If it prints an error, install them:

```sh
xcode-select --install
```

A dialog appears. Accept it and wait — this can take several minutes.

Then confirm:

```sh
git --version
python3 --version
```

You need Python 3.9 or newer for the music step. macOS system Python is 3.9,
which is fine. You do **not** need to install anything else for it — the
reference script uses only the standard library.

**Check:** `git --version` and `python3 --version` both print a version.

> **Why this matters:** a lot of "the agent is broken" reports turn out to be a
> missing command-line tool. The agent is often just surfacing an error your
> shell would have given you too.

## 1.4 Install Homebrew

```sh
brew --version
```

If that works, skip to 1.5.

If not, install it from <https://brew.sh>. The current one-liner is:

```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

On Apple silicon, Homebrew installs to `/opt/homebrew` and the installer prints
two commands to add it to your `PATH`. Run them. They look like:

```sh
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

Then open a new terminal window, or run `source ~/.zprofile`.

**Check:** in a **new** terminal window, `brew --version` prints a version and
`which brew` points at `/opt/homebrew/bin/brew` (Apple silicon) or
`/usr/local/bin/brew` (Intel).

## 1.5 Install OpenCode

```sh
brew install anomalyco/tap/opencode-v2
```

Homebrew will pull the correct binary for your architecture, so you don't need
to think about apple silicon vs Intel here.

**Check:**

```sh
opencode --version
which opencode
```

`--version` prints something like `2.x.x`, and `which` prints a path. If it
prints `command not found`, see the fix at the bottom of this page.

### Alternatives, if Homebrew isn't an option

Only pick one. Don't install twice — you'll end up running one version and
updating another.

| Method | Command |
| --- | --- |
| Install script | `curl -fsSL https://opencode.ai/v2/install \| bash` |
| npm | `npm install -g @opencode/cli` |
| Bun | `bun install -g --trust @opencode/cli` |
| pnpm | `pnpm add -g --allow-build=@opencode/cli @opencode/cli` |
| Standalone | Download the macOS zip for your architecture from <https://opencode.ai/v2/docs/> and put the binary on your `PATH` |

The npm package uses a postinstall script to select the right native binary,
which is why Bun and pnpm need the extra "allow scripts" flags. If you use one
of those and get a missing-binary error, that flag is usually why.

> Windows package managers are not supported by OpenCode. Not relevant here,
> but it comes up when a teammate on Windows asks why your setup notes don't
> work for them.

## 1.6 First launch

From your scratch directory:

```sh
cd ~/scratch
opencode
```

You should get a terminal UI. Don't type anything yet — there's no model
connected. Press `Ctrl+C` to exit (or type `/exit`).

If the UI opens but looks scrambled, make the window bigger. Terminal UIs need
room, and a narrow window is the most common cause of "the interface is
broken".

**Check:** you opened the TUI and exited cleanly.

---

## If something went wrong

### `opencode: command not found`

The install worked but your shell can't find it.

```sh
ls /opt/homebrew/bin/opencode     # Apple silicon
ls /usr/local/bin/opencode        # Intel
```

If the file exists, it's a `PATH` problem. Re-run the `brew shellenv` line from
1.4 in your shell profile and open a new terminal.

If the file doesn't exist, the install didn't finish. Re-run 1.5 and read the
output rather than assuming success.

### `Bad CPU type in executable`

You downloaded a binary for the wrong architecture. `uname -m` tells you which
you need. If you used the standalone zip, get the other one.

### `xcrun: error: invalid active developer path`

The Xcode tools were removed or moved, often by a macOS upgrade. Re-run:

```sh
xcode-select --install
```

### `brew` works but installs are very slow

That's a first-run Homebrew behaviour — it updates its package index before
installing. Later installs are faster. Don't kill it halfway; a partial install
is worse than a slow one.

---

**Next:** [Connect a model](02-connect-a-model.md)
