---
name: workspace
description: "Use `heliox workspace ...` for the active org's workspace: showing current workspace metadata, renaming it, editing description/slug, listing workspace members, and inviting teammates. Trigger whenever the assistant needs to introspect or mutate workspace-level org state (name, description, slug, members) or invite a human teammate. For the AI's own profile (display name, avatar, status) use `heliox:profile`; for runtime hosts use `heliox assistant node`."
user-invocable: false
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox workspace --help"
---

# Heliox Workspace

Start by reading `../shared/SKILL.md`.

Workspace commands act on the caller's currently active org. They require a resolvable active org id (from `HELIO_ORG_ID` or runtime credentials). For the AI's own outward-facing profile (display name / avatar / rename / status) use `heliox:profile`; for runtime host inventory use `heliox assistant node`.

## Workspace info

```bash
heliox workspace show --json
```

`workspace show` returns the active workspace's `workspace_id`, `name`, `slug`, `image_url`, `description`, and `members_count`. Use it before mutating workspace metadata or before assuming which workspace is active. There is no bare `heliox workspace` shortcut — the `show` subcommand is required.

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
heliox workspace members get <user_id> --json
heliox workspace members invite alice@example.com --json
heliox workspace members invite bob@example.com --role org:admin --json
heliox workspace members invite alice@example.com --role org:member --json
```

`members get <user_id>` returns the single workspace member with that id (display name, role, email, avatar). Use it whenever you have a user id from a system reminder — e.g. `message.sender.id` — and want the human-readable info. The `<user_id>` can be either the internal mongo id or the Clerk user id; the command paginates the member list and matches on either.

`members list` supports `--query`, `--type human|ai`, `--limit`, and `--offset`.

Invite `--role` is passed straight through to Clerk and must use the prefixed form: `org:admin` or `org:member`. Plain `admin` / `member` are rejected. Omitting `--role` defaults to `org:member` server-side.
