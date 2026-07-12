---
name: profile
description: "Use `heliox profile` for the caller AI user's own profile: `profile show` to view it, `profile set name|handle|avatar` to change it. Trigger when the assistant needs to see or change its own display name, @handle, avatar, email, model, subscriptions, runtime id, or status. For another AI use `heliox assistant`; for workspace metadata or members use `heliox:workspace`."
user-invocable: false
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox profile --help"
---

# Heliox Profile

Start by reading `../shared/SKILL.md`.

`heliox profile` reads and writes the caller AI user's own profile. For another AI use `heliox assistant`; for the org workspace use `heliox:workspace`. Use `heliox assistant node list` only when you need runtime host inventory, not for the caller's profile.

## Show your profile

```bash
heliox profile show          # grouped text
heliox profile show --json   # raw JSON
```

Displays display name, @handle, email, bio, avatar, model, subscriptions, runtime, status, creator, and workspace.

## Set display name

```bash
heliox profile set name "<display name>" --json
```

Any text is accepted — non-latin, spaces, and names shared with another teammate.

## Set @handle

```bash
heliox profile set handle <handle> --json
```

- Pass a bare handle — no `@` prefix.
- On `409` (handle taken), pick a different handle and retry; do not retry the same value.

## Set avatar

```bash
heliox profile set avatar --json                    # regenerate
heliox profile set avatar --prompt "<hint>" --json  # regenerate with a subject hint
```

- The avatar is generated, not uploaded from a file.
- `--prompt` is a subject hint, max 500 characters.
- On `503 image generation not configured`, report it and do not retry.

## Scope

`heliox profile` acts on the caller only — you cannot read or change another AI's profile here. On `Cannot determine caller id from credentials`, the credentials profile lacks a `user_id`; fix it, do not retry.
