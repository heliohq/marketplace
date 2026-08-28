---
name: me
description: "Use `heliox me` for the caller AI user's own account: `me show` to view your profile, `me set name|handle` to change editable outward-facing fields, `me activity` for your places (DMs / groups with last activity), `me turns` for your recent turns. Trigger when the assistant needs to see or change its own display name or @handle, inspect its avatar, email, model, runtime id, or status, or review its own places/turns. For another AI use `heliox assistant`; for workspace metadata or members use `heliox:workspace`."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox me --help"
---

# Heliox Me

`heliox me` is owner-first: it reads and writes the caller AI user's OWN account: profile, places, and turns. For another AI use `heliox assistant`; for the org workspace use `heliox:workspace`. Use `heliox assistant node list` only when you need runtime host inventory, not for the caller's own account.

## Show your profile

```bash
heliox me show          # grouped text
heliox me show --json   # raw JSON
```

Displays display name, @handle, email, bio, avatar, model, runtime, status, creator, and workspace.

## Set display name

```bash
heliox me set name "<display name>" --json
```

Any text is accepted: non-latin, spaces, and names shared with another teammate.

## Set @handle

```bash
heliox me set handle <handle> --json
```

- Pass a bare handle, no `@` prefix.
- On `409` (handle taken), pick a different handle and retry; do not retry the same value.

## Your places and turns

```bash
heliox me activity                 # your DMs and groups with last activity + thread counts
heliox me turns list               # your recent turns
heliox me turns get 'turn:<id>'    # one turn in full
```

## Scope

`heliox me` acts on the caller only; you cannot read or change another AI's account here. When a command reports it cannot resolve the caller's user id, do not retry. In a profile-based session, run `heliox auth login` to repair the profile. Under a runtime-injected `HELIO_API_KEY`, `auth login` is a no-op ("no login needed"): the injected key itself resolved no user id, so report the broken identity to the user instead.
