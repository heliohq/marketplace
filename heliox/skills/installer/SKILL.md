---
name: installer
description: "Install or uninstall a capability in the engine you are running inside. Trigger when the user asks to install/add or uninstall/remove a skill, plugin, or MCP server — e.g. an install prompt like `Use heliox:installer to install X (skill:foo) from source github/owner/repo@rev/path` or an uninstall prompt `Use heliox:installer to uninstall X (skill:foo)` from the read view's +/trash button. You act ENGINE-NATIVELY via the hosting engine's own CLI. INSTALL needs a SOURCE carried in the prompt — no source, FAIL FAST, never guess, never web-search. UNINSTALL needs only the machine key in the prompt — ambiguous or absent, FAIL FAST. Per-engine commands live in claude-code.md and codex.md."
metadata:
  requires:
    bins: ["heliox"]
---

# Heliox Capability Installer

Start by reading `../shared/SKILL.md`.

## Mental model

You run **inside** one engine — Claude Code or Codex. There is **no install/
uninstall verb of the runtime's own** — you drive the *hosting engine's own CLI*,
then verify and report. The prompt's verb picks the direction:

- **install** — needs a **source** (a git repo). It comes **only from the
  prompt**; there is nothing to query for it.
- **uninstall** — needs only the **machine key** of what to remove. No source, no
  git.

**Fail fast — never guess.**
- No parseable **source** on an install (user typed "install X" freehand, or
  pasted a skill with no repo) → STOP, say you cannot install without a source,
  ask for the repo (`owner/repo[@ref][/path]`) or the read view's `+` button. Do
  NOT web-search, do NOT infer from the display name, do NOT install a guess.
- No parseable **key** on an uninstall, or a key that could match more than one
  installed object → STOP and ask which exact object (by key). Display names
  collide — figma is a plugin, a bundled skill, and an MCP row — so removing "by
  name" can delete the wrong thing.

## The pipeline

**read the verb → parse the target → (missing required piece ⇒ fail fast) →
detect engine → follow the engine doc → verify → echo.** This SKILL.md owns the
engine-agnostic steps (verb, parse, detect, safety); the **per-engine command
recipes live in [claude-code.md](claude-code.md) and [codex.md](codex.md)** — read the one
for your detected engine and run its `install` or `uninstall` recipe for the
capability's kind.

## 1. Read the verb and parse the target

Every prompt names an action and a target `(\`<key>\`[, source \`<source>\`])`.

- **verb** — "install / add" ⇒ install; "uninstall / remove" ⇒ uninstall.
- **key** → the capability KIND from its prefix: `skill:…` ⇒ skill,
  `plugin:…` (or `<name>@<marketplace>`) ⇒ plugin, an MCP key ⇒ mcp_server.
- **source** (install only) = `github/<owner>/<repo>@<revision>/<path>`:
  - `<owner>/<repo>` → the git repository (e.g. `blader/humanizer`)
  - `<revision>` → the commit to pin (always pin — it must match what the read
    view echoes)
  - `<path>` → subpath inside the repo; `root` (or empty) means the repo root

Missing the piece the verb requires (source for install, unambiguous key for
uninstall) → **fail fast** (see Mental model). Do not continue.

## 2. Detect the engine, then follow its doc

In order (stop at the first that resolves):

1. `CODEX_HOME` set, or `~/.codex/config.toml` exists → **codex** → read [codex.md](codex.md).
2. `CLAUDE_CONFIG_DIR` set, or `~/.claude/` exists → **claude** → read [claude-code.md](claude-code.md).
3. `command -v codex` → codex; `command -v claude` → claude.

State the detected engine in your plan so the user can catch a misdetect. The
two engines' verbs are NOT interchangeable — never run one engine's commands on
the other. From here, follow the detected engine's doc: it has the `install` and
`uninstall` recipes (idempotency check, the kind × command mapping, and the
verify step) for that engine.

## 3. Safety (both engines)

**Install:** confirm before installing when the source is not a reviewed catalog
entry — a repo pasted by the user is unscanned: read its `SKILL.md` (frontmatter
+ any network calls, env-var reads, unrelated shell) and get an explicit OK
first. An stdio MCP server runs a local subprocess — show the exact command + env
before adding. Catalog-resolved entries pinned to a revision are lower risk; a
one-line "Install X (repo@rev) on <engine>?" confirm suffices.

**Pinning is kind-dependent — don't promise what the engine can't do.** A
git-cloned skill and a codex plugin (`codex plugin marketplace add --ref`) install
the exact `<revision>`. A **claude plugin cannot be pinned** — `claude plugin
marketplace add` clones the default branch and tracks it. So for a claude plugin,
verify the HEAD against `<revision>` if you can, and state plainly that it follows
the branch rather than claiming it's pinned.

**Uninstall:** removal is the destructive direction — name the exact object you
are about to remove (by key + engine-native id) and confirm before running, and
call out **cascades**: uninstalling a plugin also removes the skills / MCP / subagents it
bundles. Never remove by fuzzy name match.

## 4. Echo (both engines)

Report the outcome using the **stable identifier verbatim** (the catalog key +
the engine-native id from the per-engine verify step), never the display name —
display names collide. The read view's badge flips (installed ↔ gone) via runtime
observations within ~60s. Flag if a session reload is needed for a newly added or
removed skills dir.
