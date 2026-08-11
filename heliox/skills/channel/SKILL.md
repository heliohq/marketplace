---
name: channel
description: "Use Heliox channel commands for channel CRUD (create, list, show, update, delete), membership management, and attachments. Trigger whenever the assistant needs to inspect or modify a channel object, change members, or recover attachments. **Message verbs (send / cede / list / get) are under `heliox message *`** — run `heliox message --help` for that surface; do not look for them here."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox channel --help"
---

# Heliox Channel

This skill covers channel objects and their membership, not the messages flowing through them; message-plane rules — send, list, threads, cede, freshness, attachments — live in `heliox:message`.

## Commands

```bash
heliox channel list [--type dm|group] --json
heliox channel show '#engineering' --json                  # detail + inline member roster
heliox channel create '#release-notes' --type group [--description "<text>"] [--members "@alice,@bob"] [--visibility private|public] --json
heliox channel update '#engineering' [--name "core-eng"] [--description "<text>"] [--visibility private|public] --json
heliox channel delete '#engineering' --yes --json          # archives; --yes required
heliox channel members list '#engineering' --json
heliox channel members add '#engineering' '@alice' [--role admin] --json
heliox channel members set-role '#engineering' '@alice' admin|member --json
heliox channel members remove '#engineering' '@alice' --json
heliox channel attachments download '#engineering' <message-seq> --json
```

Quote `#name` in shell — bash treats unquoted `#` as a comment start and silently truncates the rest of the line.

## Addressing

Channel args accept `engineering` or `#engineering`; user args accept `alice` or `@alice`. Raw 24-hex ids are rejected everywhere, in both directions: `--members` takes handles, and if a system reminder hands you a channel id, match it against the hex inside `routeUrl` from `channel list --json` — the only place the contract carries a raw id.

Visibility values are `private|public` only; create defaults to private when the flag is omitted, so pass `--visibility` at create time instead of chaining a `channel update`.

## Reading --json

Rows are agent projections, not wire documents:

- **Channel row** (list / create / update echo): `name` (addressable — `#name` for groups; a DM row's name is the peer's display name), `type`, `visibility`, `description`, `routeUrl`. `show` adds `status`, timestamps, the member roster, and (team channels) the projected `team` contract.
- **Member row** (everywhere): one resolved `user` field (`@handle` → display name → bare id; never blank), `type` (`human|ai`; omitted only when the workspace cache can't resolve the member), `role`, and `notification_level`. `role` is a channel *permission* (`admin|member`), not a work-role. There is no `user_id` or row id.
- **member write echo** (`add` and `set-role`): `{status, channel, user, role}` — `status` is `added` | `already_member` | `updated`. `already_member` is an idempotent no-op, not a fresh write; don't retry or double-notify. It carries no `role` because the echo reports what a call WROTE and this one wrote nothing — not because the role is unknowable: the server does report the held role, and the CLI drops it. When you need it, read it from `channel members list`. `channel` and `user` come back in your own vocabulary (`#name` / `@handle`), never the resolved ids.
- **never demote the last admin**: neither `set-role` nor `remove` refuses it yet, and a channel with zero admins has nobody who can manage membership — recovery needs org-level access. Check the roster with `members list` before demoting or removing anyone holding `admin`, and promote a replacement first. This is a known gap, not a guarded operation.
- **changing a role**: use `members set-role`. Against a current server, a bare `members add` on someone already in the channel is a no-op reporting `already_member` whatever role they hold — it asks only that they be present, and never touches the role. (Against an older server that still reads an absent role as `member`, the same call errors out instead, telling you to pass `--role` or use `set-role`. Either way it never changes a role you did not name.) `members add --role X` against a member holding a different role *does* chain the change and reports `updated`, so it is not a safe "make sure they're in the channel" call; `set-role` says what you mean. Never use `remove` + `add --role`: that pair is not atomic — if the re-add fails the member is left outside the channel — and it resets the member row, moving the channel-join anchor.
- **attachments download**: the downloaded files — `path`, `source_ref`, `bytes` per attachment. This verb is what puts an attachment on disk; nothing pre-materializes one, so `path` is the first place the file exists. Files land under the store root at `attachments/<#channel|@handle>-<channel-id>/<message-seq>/` — read `path` rather than reassembling it. `<message-seq>` is the per-channel seq from any `message list` read (text rows lead with it; never a mongo message id), and the attachment target accepts `#<name>` or `@<handle>` like message verbs.

## Judgment

Delete channels sparingly — only ones whose lifecycle you own, and only with explicit cause; `--yes` acknowledges the archive.
