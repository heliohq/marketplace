# Claude Code — install / uninstall recipes

Read [SKILL.md](SKILL.md) first (verb, parse, detect, safety, echo). You are on
**Claude Code**. For install, `OWNER_REPO` = `<owner>/<repo>` and `REV` =
`<revision>` from the parsed source. Pick the section by the key's kind, then run
the `install` or `uninstall` block per the prompt's verb.

## skill (`skill:…`)

There is no `claude skill` subcommand — a skill is just a folder with `SKILL.md`
at its root under `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/<name>`.

**Install** — idempotent **by revision**: if the skill dir already exists,
compare its revision marker to `$REV`; equal → "already installed", stop;
different → replace it so a bumped catalog revision actually lands. The clone
goes to a temp dir and only the requested `<path>` subtree (root ⇒ whole repo) is
copied in, so a non-root source like `.../skills/foo` installs with its
`SKILL.md` at the destination root.

```bash
DEST="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/<name>"
# Revision marker survives the subpath copy (which drops the repo's .git).
if [ "$(cat "$DEST/.helio-skill-rev" 2>/dev/null)" = "$REV" ]; then
  echo "already installed at $REV"; exit 0
fi
rm -rf "$DEST"
TMP="$(mktemp -d)"
git clone --depth 1 "https://github.com/${OWNER_REPO}.git" "$TMP"
( cd "$TMP" && git fetch --depth 1 origin "$REV" && git checkout "$REV" )
# SUBPATH is the parsed <path>; "root"/empty means the repo root.
SRC="$TMP"; [ -n "<path>" ] && [ "<path>" != "root" ] && SRC="$TMP/<path>"
mkdir -p "$DEST" && cp -R "$SRC"/. "$DEST"/ && rm -rf "$TMP"
printf '%s' "$REV" > "$DEST/.helio-skill-rev"
test -f "$DEST/SKILL.md" || { echo "SKILL.md not at root — check the source <path>"; exit 1; }
```

**Uninstall** — remove the folder. Not there → report "not installed" and stop.
Never remove a skill dir that belongs to a plugin (path under `.../plugins/…`) —
uninstall the plugin instead.

```bash
DEST="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/<name>"
test -d "$DEST" || { echo "not installed"; exit 0; }
rm -rf "$DEST"
```

A newly added or removed skills dir may need a session reload before Claude Code
notices — say so in your echo.

**Verify:** install → `test -f "$DEST/SKILL.md"`; uninstall → `test ! -e "$DEST"`.

## plugin (`plugin:…`, or `<name>@<marketplace>`)

**Install** — the repo ships `.claude-plugin/marketplace.json`. Register the
marketplace, then install. Read the marketplace NAME back — do not guess it.
Idempotent: `claude plugin list --json` already shows it → stop.

```bash
claude plugin marketplace add "$OWNER_REPO"   # clones the repo's DEFAULT BRANCH — no --ref
claude plugin marketplace list                # read the registered <marketplace> name
claude plugin install "<name>@<marketplace>" --scope user
```

`marketplace add` is idempotent; re-adding the same source is safe (still read
`marketplace list` first to reuse the existing name).

**No revision pinning for claude plugins.** `claude plugin marketplace add` takes
no commit/ref — it clones the default branch HEAD, so the plugin **tracks that
branch** and a later `marketplace update` floats to new HEAD. `$REV` cannot pin
it. Use `$REV` only to *verify* what you got (`git -C ~/.claude/marketplaces/<mkt>
rev-parse HEAD` and compare), and **tell the user the plugin is not pinned** — it
follows the branch, unlike a git-cloned skill or a codex plugin (`--ref`).

**Uninstall** — remove the plugin by its `<name>@<marketplace>` ref. This
**cascades**: the plugin's bundled skills / MCP servers / subagents go with it —
say so before running. Leave the marketplace registered (other plugins may use
it). Not installed → report and stop.

```bash
claude plugin list --json                 # confirm the exact <name>@<marketplace>
claude plugin uninstall "<name>@<marketplace>"
```

**Verify:** `claude plugin list --json` — install → present; uninstall → gone.

## mcp_server

- **figma** (and any provider whose connect flow says "do not use `mcp add`"):
  do NOT `mcp add`/`mcp remove` it here. Surface the engine connect guide
  (`heliox tool figma`) and route the user through connect/disconnect.
- **Generic HTTP/stdio MCP:**
  ```bash
  # install / connect
  claude mcp add --transport http --scope user <name> <URL>        # HTTP (OAuth-capable)
  claude mcp add --scope user [-e KEY=v ...] <name> -- <command> [args...]   # stdio subprocess — confirm first, §Safety
  claude mcp login <name>     # if OAuth is required
  # uninstall / remove
  claude mcp remove --scope user <name>
  ```

**Verify:** `claude mcp get <name>` — install → shows server + auth/health;
uninstall → not found.
