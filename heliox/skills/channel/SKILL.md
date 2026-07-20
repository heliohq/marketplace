---
name: channel
description: "Use Heliox channel commands for channel CRUD (create, list, show, update, delete), membership management, attachments, and opening solo coding sessions. Trigger whenever the assistant needs to inspect or modify a channel object, change members, recover attachments, or open a solo coding environment. **Message verbs (send / cede / list / get) are under `heliox message *`** — run `heliox message --help` for that surface; do not look for them here."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox channel --help"
---

# Heliox Channel

Start by reading `../shared/SKILL.md`; it owns routing, JSON, thread, attachment, and freshness rules.

This skill covers **channel objects and their membership**, not messages flowing through them. For sending / listing / acknowledging messages, run `heliox message --help`.

## Addressing

Every CRUD verb here accepts the channel in two equivalent shapes:

- bare name — `engineering`
- `#`-prefixed — `#engineering`

24-hex ids are rejected; reverse-lookup via `heliox channel list --json` if all you have is an id.

`@`-prefixed inputs are rejected (those are user handles, see `heliox:assistant` or `heliox:workspace`).

## CRUD

```bash
heliox channel list --json
heliox channel list --type group --json
heliox channel list --type dm --json
heliox channel list --type solo --json
heliox channel show '#engineering' --json
heliox channel create '#release-notes' --type group --json
heliox channel create '#release-notes' --type group --description "<text>" --members "user_a,user_b" --json
heliox channel update '#engineering' --name "core-eng" --json
heliox channel update '#engineering' --description "<text>" --json
heliox channel update '#engineering' --visibility public --json
heliox channel delete '#engineering' --yes --json
```

Quote `#name` in shell — bash treats unquoted `#` as the start of a comment and silently truncates the rest of the line.

`channel create` takes the name as a positional arg, not a flag. Channel type comes from `--type solo|dm|group`. There is no `--private` flag — visibility is set via `channel update --visibility private`.

Delete channels sparingly. `--yes` is required to confirm the destructive action. Only delete channels whose lifecycle you own, such as a solo runtime channel you created and no longer need.

## Members

```bash
heliox channel members list '#engineering' --json
heliox channel members add '#engineering' '@alice' --json
heliox channel members add '#engineering' '@alice' --role admin --json
heliox channel members remove '#engineering' '@alice' --json
```

Channel arg accepts bare or `#`-prefixed; user arg accepts bare or `@`-prefixed. `members add --role` defaults to `member`; pass `--role admin` to grant channel-admin.

## Attachments

```bash
heliox channel attachments download '#engineering' <message-seq> --json
heliox channel attachments download @alice          <message-seq> --json
```

Address the channel by `#<name>` (group) or `@<handle>` (DM) — resolved the same way as `message list`/`send`. `<message-seq>` is the per-channel seq from `message list --json` (not the mongo message id).

## Solo coding environments

When work needs code changes, tests, or commands, open a solo coding channel instead of writing code inline:

```bash
heliox channel create '#<short-brief>' --type solo --initial-prompt "<brief>" --json
```

Rules:

- `--initial-prompt` is the full work order: what to do, why, constraints, tests, and what done means.
- The response is the new channel row; the `id` is the addressable handle for solo channels (see follow-up note below).
- Before opening a new coding environment, check whether an existing solo channel already has the context:

```bash
heliox channel list --type solo --json
```

> **Solo follow-up gap (2026-05)**: the workspace resolver cache only indexes group channels by name, so `heliox message send '#<solo-name>' "<text>" --seen <seq>` and `heliox message list '#<solo-name>'` both miss the cache and fail. Until the cache is extended to cover solo channels, the practical path for follow-ups is: capture the new solo channel's `id` from the create response (`--json`) and either (a) wait for solo workflow to complete autonomously, or (b) ask the user to drive subsequent input via the desktop app. Treat solo channels as fire-and-observe from the brain's side.
