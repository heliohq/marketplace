---
name: workspace
description: "Use `heliox workspace ...` for the active org's workspace: showing current workspace metadata, renaming it, editing description/slug, listing workspace members, and inviting teammates. Trigger whenever the assistant needs to introspect or mutate workspace-level org state (name, description, slug, members) or invite a human teammate. For the AI's own profile (display name, avatar) use `heliox:profile`; for runtime / brain-fragment state use `heliox:status`."
user-invocable: false
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox workspace --help"
---

# Heliox Workspace

Start by reading `../shared/SKILL.md`.

Workspace commands act on the caller's currently active org. They require a resolvable active org id (from `HELIO_ORG_ID` or runtime credentials). For the AI's own outward-facing profile (display name / avatar / rename) use `heliox:profile`; for runtime / brain-fragment state use `heliox:status`.

## Workspace info

```bash
heliox workspace show --json
heliox workspace --json
```

`workspace show` (also reachable as bare `heliox workspace`) returns the active workspace's `workspace_id`, `name`, `slug`, `description`, and `members_count`. Use it before mutating workspace metadata or before assuming which workspace is active.

## Workspace metadata

```bash
heliox workspace set name "<workspace name>" --json
heliox workspace set description "<text>" --json
heliox workspace set description "" --json
heliox workspace set slug "<slug>" --json
```

Pass an empty string to `set description` to clear it. Slug must be unique across the org's URL namespace; the backend rejects collisions.

## Workspace members

```bash
heliox workspace members list --json
heliox workspace members list --type human --json
heliox workspace members list --type ai --json
heliox workspace members list --query "alice" --json
heliox workspace members list --limit 25 --offset 25 --json
heliox workspace members invite alice@example.com --json
heliox workspace members invite bob@example.com --role admin --json
```

`members list` (also reachable as bare `heliox workspace members`) supports `--query`, `--type human|ai`, `--limit`, and `--offset`. When the result is paged, the non-JSON output prints the next `--offset` to use.

Invite roles are `member` or `admin`. The CLI maps them to Clerk roles internally.
