---
name: skill
description: "Use `heliox skill ...` to install, list, show, or uninstall standalone skills for this assistant (design 214). Trigger when the user asks to add a skill from a local file, directory, zip, GitHub repo/path, or raw SKILL.md content, or asks 'what skills do I have' / 'remove the X skill'."
user-invocable: false
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox skill --help"
---

# Heliox Skill

Start by reading `../shared/SKILL.md`.

This skill teaches you to manage standalone skills installed on the current assistant: install, list, show, uninstall. Standalone skills are SKILL.md files (with optional helper files) the user — or you — adds at runtime. They survive across pod restarts and show up as `/skill-name` in claude or as catalog entries in codex.

## Input shapes heliox accepts

`heliox skill install <path|github-source>` accepts ONE input, auto-detected by shape:

| Input | What heliox does | Use case |
|---|---|---|
| **Directory** (`./my-skill/`) | Walks + zips on the fly, uploads multipart. SKILL.md must be at the root of the dir OR inside a single top-level subdir. | Skill with reference files (templates, helper docs) |
| **`.zip` archive** (`./my-skill.zip`) | Uploads as-is. Same SKILL.md placement rules. | Pre-packaged or shared skill |
| **Single `.md` file** (`./SKILL.md`) | Reads the body, uploads inline as JSON. | Simplest skill — frontmatter + body only, no helpers |
| **GitHub source** (`owner/repo`, `github.com` URL, `/tree/<ref>/<path>` URL, `/blob/<ref>/<path>/SKILL.md` URL) | Sends the source to backend. Backend fetches exactly one selected repo directory, validates root `SKILL.md`, stores a zip, and the runtime later pulls that stored zip. | Public GitHub skill repos and curated repo/path installs |

heliox does not install a whole repo by scanning for many skills. A bare GitHub repo means the repo root must contain `SKILL.md`. A `/tree/<ref>/<path>` URL or `--path <path>` selects exactly one directory, and that directory must contain `SKILL.md`. A `/blob/<ref>/<path>/SKILL.md` URL selects the containing directory.

## SKILL.md frontmatter

Every skill must have YAML frontmatter declaring `name` and `description`:

```yaml
---
name: my-skill
description: "What the skill does and when to use it"
---
```

`name` must match `^[a-z0-9][a-z0-9-]{0,62}$`. `description` is what claude/codex see when ranking which skill to load — keep it action-oriented and include trigger phrases the user might say.

There is no `--name` override. Name and description should come from `SKILL.md`; local uploads reject missing `name` or `description`, and URL installs always require a description.

## Backend validation

There are no size caps, file-count caps, or extension whitelists on skill uploads. Ship `.md`, `.py`, `.sh`, `.png`, reference data, helper templates — whatever the skill needs. JuiceFS per-user quotas bound disk use.

The backend only rejects structural bugs that would corrupt unrelated files:

- Zip-slip paths (any entry escaping the skill dir)
- Symlinks inside an upload
- Missing `SKILL.md` at the root
- Empty `name` or `description` in frontmatter (these are load-bearing for the runtime)

## Install commands

```bash
# Directory
heliox skill install ./my-skill --json

# Zip
heliox skill install ./my-skill.zip --json

# Single SKILL.md
heliox skill install ./SKILL.md --json

# Return immediately without waiting for the runtime to converge
heliox skill install ./my-skill --no-wait --json

# Longer wait for slow runtimes (default 120s)
heliox skill install ./my-skill --timeout 5m --json

# GitHub source: root SKILL.md
heliox skill install owner/repo --json

# GitHub source: exact skill directory
heliox skill install https://github.com/owner/repo/tree/main/skills/my-skill --json
heliox skill install https://github.com/owner/repo/blob/main/skills/my-skill/SKILL.md --json
heliox skill install owner/repo --ref main --path skills/my-skill --json
```

`install` returns the row in `pending` status, then polls until `installed` or `failed` (or the timeout fires). With `--no-wait` it returns `pending` immediately — useful for fire-and-forget or batch installs. **When you run this from inside a turn (in-runtime), it auto-queues and returns `pending` without waiting**: waiting would deadlock, since the install can only finish after your tool call returns. The skill lands on the next reconcile.

## Installing from a URL

GitHub repo URLs, tree URLs, and blob URLs that point directly at `SKILL.md` can go to `heliox skill install`; backend fetches and stores the selected skill directory. Raw files, gists, and GitHub blob URLs that do not end in `SKILL.md` are not repo-directory installs, so fetch those locally first.

Always inspect a downloaded local `SKILL.md` before installing it — at minimum check the frontmatter is sensible and the body doesn't contain instructions you wouldn't run.

### Raw SKILL.md URL (gist, raw GitHub, etc.)

```bash
# Save to a workspace temp dir, then install
mkdir -p /tmp/skill-dl && cd /tmp/skill-dl
curl -fsSL "<url>" -o SKILL.md
# Inspect first — never install a SKILL.md you haven't read
cat SKILL.md
heliox skill install ./SKILL.md --json
```

### GitHub blob URL (`https://github.com/owner/repo/blob/<ref>/path/to/SKILL.md`)

Pass the blob URL directly when it points at `SKILL.md`:

```bash
heliox skill install https://github.com/owner/repo/blob/<ref>/path/to/SKILL.md --json
```

### GitHub repo URL pointing at a skill directory (`https://github.com/owner/repo/tree/<ref>/skills/<name>`)

Pass the tree URL directly:

```bash
heliox skill install https://github.com/owner/repo/tree/<ref>/skills/<name> --json
```

For a bare GitHub repo URL or `owner/repo`, use it only when the repo root itself contains `SKILL.md`:

```bash
heliox skill install owner/repo --json
```

### Private repos

Use `gh` to authenticate:

```bash
gh repo clone owner/private-repo /tmp/private-skill
cat /tmp/private-skill/skills/<name>/SKILL.md
heliox skill install /tmp/private-skill/skills/<name> --json
```

If `gh auth status` shows the agent isn't logged in, ask the user to run `gh auth login` themselves — do not store credentials.

### When the URL is ambiguous

If the user shares a bare repo URL and the repo root does not contain `SKILL.md`, list the candidates and confirm the exact directory before installing:

```bash
find /tmp/skill-src -name SKILL.md -not -path "*/node_modules/*"
```

Report the matches back to the user — don't install a guessed one.

## List, show, uninstall

```bash
heliox skill list --json
heliox skill list --status installed --json
heliox skill list --status pending --json
heliox skill list --status failed --json
heliox skill show <skill_id> --json
heliox skill uninstall <skill_id>
```

The `id` from `list --json` (NOT the name) is what `show` / `uninstall` accept. Names are not unique enough as identifiers — the backend ID is.

Uninstall is immediate and has no confirmation flag at the CLI. The runtime reconciler reaps the engine-home projection on its next pass (≤ 45 s) AND rewrites every persisted session JSONL to drop the skill from the listing.

## Status semantics

| Status | Meaning | Agent action |
|---|---|---|
| `pending` | Backend accepted the row; runtime hasn't projected yet | Wait (or `--no-wait` already returned this) |
| `installed` | Engine-home has the skill; next claude/codex session sees it | Acknowledge to user; skill is ready to use |
| `failed` | Runtime rejected (e.g. SKILL.md unparseable, name conflict, disk error) | Read `error` field via `heliox skill show <id>`; surface to user; do not retry without a fix |

After `installed`, claude's mid-session refresh rewrites the current session's JSONL so the skill becomes invokable as `/skill-name` without restarting the channel. Codex picks up new skills on its next subprocess spawn (per-turn).

## Common errors

heliox surfaces backend error codes in the JSON envelope. Map them to action:

| Error code | Cause | Fix |
|---|---|---|
| `invalid_frontmatter` | SKILL.md missing the `---` fence, or no `name` / `description` in frontmatter | Add `---\nname: ...\ndescription: ...\n---` at the top |
| `invalid_skill_name` | Skill name is empty or contains `/` or `..` (path-traversal sequence) | Pick a non-empty name without slashes or `..` |
| `already_exists` | A skill with this name already exists for this assistant | Uninstall the old one first OR rename in the SKILL.md |
| `invalid_zip` | Zip contains a path escaping the skill dir, has a symlink, or extraction failed | Repackage with cleaner relative paths; no symlinks |
| `invalid_body` | Malformed JSON / missing multipart file part / unparseable body | Check the input shape — file present? JSON well-formed? |
| `upload_not_supported` | Backend storage not configured (rare; misconfigured environment) | Report to the user; not retryable |

When the row ends in `status: failed` (post-install), `heliox skill show <id> --json` carries the runtime's error string in the `error` field. Read it before retrying.

Never retry the same failing install unchanged — fix the cause first.

## When to install proactively

Install a new skill when:

- The user explicitly shares one (file path, URL, gist).
- A pattern you handle repeatedly across turns would compress better as a skill (then ask the user before installing one you authored yourself).

Do not install:

- Skills the user didn't ask for, unless you've explained what you're about to install and they agreed.
- Skills from URLs whose SKILL.md you haven't inspected.
- Skills whose body contains instructions you wouldn't otherwise follow (a SKILL.md is an instruction set the model will read on every relevant turn).

## What lives where

After install:

- Skill source: `<brain>/.brain/skills/<name>/` (JuiceFS-backed, survives pod restarts)
- Engine projection: `<brain>/.claude/skills/<name>` (symlink → above) or `<brain>/.codex/skills/<name>/` (copied dir)
- Backend row: `assistant_skills` collection, addressable via `heliox skill show <id>`

The runtime reconciler (helio-runtime) keeps these three in sync. You don't need to touch the disk paths directly — `heliox skill *` is the only supported interface.
