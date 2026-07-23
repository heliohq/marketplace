---
name: workspace
description: "Use `heliox workspace ...` for the active org's workspace: showing current workspace metadata, renaming it, editing description/slug, listing workspace members, and inviting teammates. Trigger whenever the assistant needs to introspect or mutate workspace-level org state (name, description, slug, members) or invite a human teammate. For the AI's own profile (display name, avatar, status) use `heliox:me`; for runtime hosts use `heliox assistant node`."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox workspace --help"
---

# Heliox Workspace

Workspace commands act on the caller's currently active org. They require a resolvable active org id (from `HELIO_ORG_ID` or runtime credentials). For the AI's own outward-facing profile (display name / avatar / rename / status) use `heliox:me`; for runtime host inventory use `heliox assistant node`.

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

Pick the command from the job in front of you:

| You have / you want | Run |
| --- | --- |
| "Who is in this workspace?" / "Is X a member?" | `heliox workspace members list` |
| A raw user id (e.g. `message.sender.id` from a system reminder) | `heliox workspace members get <user_id> --json` |
| Fields to act on: email, status, bio, your own role | `heliox workspace members list --json` |
| Only AIs / only humans, or a name/email search | add `--type ai\|human` / `--query "<substring>"` |
| Bring a human into the workspace | `heliox workspace members invite <email> [--role org:admin\|org:member]` |

```bash
heliox workspace members list
heliox workspace members list --type ai --json
heliox workspace members list --query "alice"
heliox workspace members get <user_id> --json
heliox workspace members invite alice@example.com --json
heliox workspace members invite bob@example.com --role org:admin --json
```

`members list` always returns the complete roster in one call — there is no paging and no `--limit`/`--offset` flags. That completeness is a guarantee you can lean on: someone absent from the list is **not a member of this workspace** — answer accordingly, no re-query or hedging needed. One freshness caveat: the roster is served from a short (~5 min) server-side cache, so if the human says they *just* invited or removed someone and your list disagrees, trust their claim over the snapshot and re-check shortly instead of contradicting them. Prefer the plain text table for who's-here questions; it is a fraction of the tokens of `--json` and greps cleanly by `@handle`.

Member ids never appear in `list` output (in either mode). To turn an id you were handed into a person, use `members get <user_id>` — it accepts the internal mongo id or the Clerk user id. Grepping `list` output for an id will silently match nothing; that means your approach is wrong, not that the user is unknown.

`--json` member rows carry exactly what you can act on: `handle` (your addressing vocabulary — every verb takes `@<handle>`), `name`, `type` (human|ai), `role`, `status`, `email`, and `bio` when set. Raw platform ids and avatar URLs are intentionally absent. The list envelope also carries `viewer_role` — YOUR own org role; read it before admin-gated actions (invites with `--role`, role changes) instead of discovering a denial from the error.

A `status` other than `active` means the member cannot act in the workspace yet — typically an invitee who accepted but hasn't finished activation. Such rows have no `@handle`, so handle-addressed verbs (DM, mention, assign, channel add) cannot reach them; if you need that person, tell the human they must finish signing in first.

Invite `--role` is passed straight through to Clerk and must use the prefixed form: `org:admin` or `org:member`. Plain `admin` / `member` are rejected. Omitting `--role` defaults to `org:member` server-side.
