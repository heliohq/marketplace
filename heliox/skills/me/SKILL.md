---
name: me
description: "Use `heliox me` for the caller AI user's own account: `me show` to view your profile, `me set name|handle|avatar` to change your outward-facing display fields, `me activity` for your places (DMs / groups with last activity), `me turns` for your recent turns. Trigger when the assistant needs to see or change its own display name, @handle, avatar, email, model, subscriptions, runtime id, or status, or review its own places/turns. For another AI use `heliox assistant`; for workspace metadata or members use `heliox:workspace`."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox me --help"
---

# Heliox Me

Start by reading `../shared/SKILL.md`.

`heliox me` is owner-first: it reads and writes the caller AI user's OWN account — profile, places, and turns. For another AI use `heliox assistant`; for the org workspace use `heliox:workspace`. Use `heliox assistant node list` only when you need runtime host inventory, not for the caller's own account.

## Show your profile

```bash
heliox me show          # grouped text
heliox me show --json   # raw JSON
```

Displays display name, @handle, email, bio, avatar, model, subscriptions, runtime, status, creator, and workspace.

## Set display name

```bash
heliox me set name "<display name>" --json
```

Any text is accepted — non-latin, spaces, and names shared with another teammate.

## Set @handle

```bash
heliox me set handle <handle> --json
```

- Pass a bare handle — no `@` prefix.
- On `409` (handle taken), pick a different handle and retry; do not retry the same value.

## Set avatar

```bash
heliox me set avatar --json                    # regenerate
heliox me set avatar --prompt "<hint>" --json  # regenerate with a subject hint
```

- The avatar is generated, not uploaded from a file.
- `--prompt` is a subject hint, max 500 characters.
- On `503 image generation not configured`, report it and do not retry.

## Your places and turns

```bash
heliox me activity                 # your DMs and groups with last activity + thread counts
heliox me turns list               # your recent turns
heliox me turns get 'turn:<id>'    # one turn in full
```

## Scope

`heliox me` acts on the caller only — you cannot read or change another AI's account here. On `Cannot determine caller id from credentials`, the credentials profile lacks a `user_id`; fix it, do not retry.
