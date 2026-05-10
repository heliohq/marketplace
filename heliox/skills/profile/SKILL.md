---
name: profile
description: "Use `heliox profile ...` for the caller AI user's own outward-facing profile: showing the assistant's display name, email, avatar, model, and type, and renaming its display name. Trigger whenever the assistant needs to look up its own profile, find its own ai user id without spelunking env vars, or rename itself. For runtime / brain-fragment state, use `heliox:status`. For workspace-level metadata or members, use `heliox:workspace`. For external adapter (Lark / Slack / WeChat) connection state, use `heliox:assistant`."
user-invocable: false
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox profile --help"
---

# Heliox Profile

Start by reading `../shared/SKILL.md`.

This skill covers the caller AI user's outward-facing profile — what other org members see when they look at this assistant: display name, email, avatar, model, type. For runtime / brain-fragment hashes use `heliox:status`; for the org workspace use `heliox:workspace`; for external adapter (Lark / Slack / WeChat) connection state use `heliox:assistant`.

## Show

```bash
heliox profile show --json
heliox profile --json
```

`profile show` (also reachable as bare `heliox profile`) returns the caller AI user's own profile:

- `id` — internal AI user id (use this when another command takes `--ai-user-id`)
- `name` — display name (sourced from Clerk `public_metadata.display_name` per design 119)
- `email`
- `avatar` — Clerk-hosted URL when a custom image is set
- `avatar_status`
- `type` — typically `ai`
- `model` — current model id

Use this whenever a turn needs "what's my own AI user id / display name?" without grepping environment variables, or before mutating a profile field so you can show the user a before/after.

## Set name

```bash
heliox profile set name "<display name>" --json
```

Renames the caller AI user. Per design 119 the handler synchronously writes Clerk `public_metadata.display_name` (the resolver's source of truth) and best-effort mirrors `first_name` for the Clerk dashboard / SCIM exports. Identity resolver read priority is `public_metadata.display_name > first_name > username`.

`profile set name` is the only set-field today; `bio`, `timezone`, `username`, and `avatar` are intentionally parked until a real need surfaces (per design 118 D6 — `<noun> set <field> <value>` grammar). Both commands require runtime credentials with a resolvable `user_id`.

## Auth and self-only

Profile commands target the caller's own ai user id. Per design 118 D5 the backend `PATCH /users/ai/:id` enforces self-only for AI callers — an AI cannot rename a different AI through this surface; admin-scoped mutations (model / subscriptions) require a human admin going through the desktop UI.

If `heliox profile show` exits non-zero with "Cannot determine caller id from credentials", the runtime credentials profile lacks a resolvable `user_id` — fix that before retrying instead of looping.
