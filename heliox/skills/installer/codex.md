# Codex — install / uninstall recipes

Read [SKILL.md](SKILL.md) first (verb, parse, detect, safety, echo). You are on
**Codex**. For install, `OWNER_REPO` = `<owner>/<repo>` and `REV` = `<revision>`
from the parsed source. Pick the section by the key's kind, then run the
`install` or `uninstall` block per the prompt's verb.

Codex's plugin verbs are **`add`** / **`remove`**, not `install` / `uninstall` —
do not borrow Claude Code's verbs.

## skill (`skill:…`)

There is no `codex skill` subcommand — a skill is a folder with `SKILL.md` at its
root. Codex's canonical, portable skills root is `$HOME/.agents/skills`.

**Install** — idempotent **by revision**: if `$HOME/.agents/skills/<name>` already
exists, compare its checked-out commit to `$REV`; equal → "already installed",
stop; different → the pinned catalog revision moved, so replace it (below) rather
than leaving the old skill active. The clone lands in a temp dir and only the
requested `<path>` subtree (root ⇒ whole repo) is copied in, so a non-root source
like `.../skills/foo` installs with its `SKILL.md` at the destination root.

```bash
DEST="$HOME/.agents/skills/<name>"
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
Never remove a skill dir that a plugin owns — remove the plugin instead.

```bash
DEST="$HOME/.agents/skills/<name>"
test -d "$DEST" || { echo "not installed"; exit 0; }
rm -rf "$DEST"
```

A newly added or removed skills dir may need a session reload before Codex
notices — say so in your echo.

**Verify:** install → `test -f "$DEST/SKILL.md"`; uninstall → `test ! -e "$DEST"`.

## plugin (`plugin:…`, or `<name>@<marketplace>`)

**Install** — **check installed state FIRST, then register + add.** If `codex
plugin list --json` already shows the plugin, **stop** — this is the general
idempotency rule, and it is also how codex's built-in marketplaces are handled:
`openai-curated` / `openai-bundled` / … ship their plugins **pre-installed**, so a
curated target is already present and needs nothing. Never `marketplace add` a
codex-reserved marketplace name — it collides with the built-in. Only when the
plugin is absent do you register the marketplace (pinned to the revision), read
its NAME back — do not guess — then `add`:

```bash
codex plugin list --json                                 # already present (incl. built-ins)? → stop
codex plugin marketplace add "$OWNER_REPO" --ref "$REV"   # --ref pins the snapshot
codex plugin marketplace list --json                      # read the registered <marketplace> name
codex plugin add "<name>@<marketplace>"
```

Codex loads only `skills / mcpServers / hooks / apps` from a plugin. A
Claude-authored plugin still adds under Codex, but its commands / subagents / lsp
are silently inert — expected, not an error.

**Uninstall** — remove the plugin by its `<name>@<marketplace>` ref. This
**cascades**: the plugin's bundled skills / MCP servers / hooks go with it — say
so before running. Leave the marketplace registered. Not installed → report and
stop.

```bash
codex plugin list --json                  # confirm the exact <name>@<marketplace>
codex plugin remove "<name>@<marketplace>"
```

**Verify:** `codex plugin list --json` — install → present; uninstall → gone.

## mcp_server

- **figma** (and any provider whose connect flow says "do not use `mcp add`"):
  do NOT `mcp add`/`mcp remove` it here. Surface the engine connect guide
  (`heliox tool figma`) and route the user through connect/disconnect.
- **Generic HTTP/stdio MCP:**
  ```bash
  # install / connect
  codex mcp add <name> --url <URL> [--bearer-token-env-var <ENV>]            # HTTP
  codex mcp add <name> --env KEY=VALUE -- <command> [args...]                # stdio subprocess — confirm first, §Safety
  codex mcp login <name>     # OAuth streamable-HTTP servers
  # uninstall / remove
  codex mcp remove <name>
  ```

**Verify:** `codex mcp get <name> --json` — install → shows server + status;
uninstall → not found.
