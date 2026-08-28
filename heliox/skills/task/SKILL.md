---
name: task
description: "Use `heliox task ...` for Helio task lifecycle: creating, listing, showing, updating status, assigning, commenting on, or deleting tasks. Trigger whenever a task number, task card, task assignment, status transition, or task comment is part of the job."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox task --help"
---

# Heliox Task

## Model

- Tasks are org-scoped. Every verb addresses them by key (`HEL-415`) or 24-hex ObjectID; the key prefix is server-assigned.
- Set the channel at create or never: `--channel` is optional (omit it for an org-level task), takes `#name` or `@handle` (files the task into that DM), and is immutable after create.
- Status: `open | in_progress | blocked | in_review | done | cancelled`. `blocked` means stuck and still needing attention, not closed; `in_review` means the work is finished and awaiting the requester's acceptance (move a task there when you consider it done but someone else should verify; the transition notifies them). Priority (optional): `low | normal | high | urgent`. Deadlines: RFC3339 (`2026-05-20T17:00:00Z`, stored UTC). Labels: comma-separated freeform strings.
- Reads (`list` / `show`): plain text is the cheap recall mode, a fraction of the JSON tokens; add `--json` when you need `routeUrl`, description structure, or field values to act on. Writes: always `--json`. Helio renders structured task cards from it.

## List

```bash
heliox task list                                     # cheap recall read: KEY STATUS PRIO DUE ASSIGNEE TITLE
heliox task list --status in_progress --assignee @alice   # --assignees "@alice,@bob" for a set
heliox task list --channel '#engineering'
heliox task list --since 2026-07-21T00:00:00Z --json # updated in a window, ALL statuses
heliox task list --all                               # include recently closed
```

Flag values are sigiled (`@handle` / `#name`); 24-hex ids are rejected. The bare list is a bounded page of ACTIVE tasks (open / in_progress / blocked / in_review, newest 50; `--limit 0` rejected); `--all` adds recently closed, `--cursor <next_cursor>` pages further.

JSON rows carry your vocabulary: `key` (the verb address), `routeUrl` (the `https://app.helio.im/task/...` share URL; paste it as `[HEL-415](routeUrl)`), and `assignee`/`channel` resolved to `@handle`/`#name`. A bare name or hex there means the cache had no mapping: it is display-only; resolve via `workspace members` before using it in a command. `create`/`update` echo this same row shape; verify a description with `task show`.

## Create

```bash
heliox task create "<title>" --json                  # org-level task, no channel
heliox task create "<title>" --channel '#engineering' --json
heliox task create "<title>" --channel '#engineering' --assignee @alice --priority high --deadline 2026-05-20T17:00:00Z --labels frontend,perf --json
heliox task create "<title>" --channel '#engineering' -d "<markdown body>" --json
heliox task create "Visual bug" --channel '#engineering' -a ./shot1.png -a ./shot2.png --json
```

Write `-d/--description` as Markdown; the CLI renders headings, lists, code, and links as rich text and wraps the result into the Tiptap wire doc; never pass Tiptap JSON. `-a/--attachment` (repeatable) uploads files: image refs embed inline in the description (`![name](helio://attachment/...)`, after any `-d` paragraphs), non-image refs ride `attachments[]`; both surface as `attachments[].uri`, fetchable via `heliox blob get` (see `heliox:message` §Attachments).

## Show

```bash
heliox task show <id-or-key> --json
heliox task show <id-or-key> --activity --json   # + activity log, last 20 changes
```

The response inlines the full picture: `task.description` (Tiptap; image nodes carry `attrs.src = "helio://attachment/..."`), `task.attachments[]` and `comments[].attachments[]` (each with a `uri`), and `activities[]` when requested.

## Update

```bash
heliox task update <id-or-key> --title "<new>" --status done --assignee @alice --priority urgent --json
heliox task update <id-or-key> -d "<new markdown body>" --json
heliox task update <id-or-key> -a ./new-shot.png --clear-description --json
```

Flags: `--title`, `--status`, `--assignee`, `-d`, `--priority`, `--deadline`, `--labels`, `-a`, `--clear-attachments`, `--clear-description`. Omitted or empty flags preserve the current value; reassigning needs a real `@handle`.

Attachments are tri-state: omit both flags = unchanged; `-a file...` = upload and REPLACE the whole set; `--clear-attachments` = drop all (the two are mutually exclusive). Because image refs live inside the description, any attachment replacement must also decide the description: pair `-a`/`--clear-attachments` with either `--clear-description` or `-d "<new prose>"`, and keep any `helio://attachment/...` refs in a new `-d` consistent with the new attachment set; mismatches are rejected server-side.

## Done (close with evidence)

```bash
heliox task done <id-or-key> --comment "<what was done, with evidence>" --json
heliox task done <id-or-key> --json
```

One verb for the dominant ending: the evidence comment posts FIRST (a failed
comment aborts and leaves the task open), then the status flips to done,
equivalent to `comments add` + `update --status done` in one call.

## Comments

```bash
heliox task comments list <id-or-key> --json
heliox task comments add <id-or-key> "<body>" --json
heliox task comments add <id-or-key> -a ./repro.log --json            # attachment-only is valid
heliox task comments add <id-or-key> "<body>" --parent <comment_id> --json
heliox task comments update <id-or-key> <comment_id> "<new body>" --json
heliox task comments delete <id-or-key> <comment_id> --yes --json
```

Comments are the task's durable evidence; channel messages are conversation. `comments update` follows the same tri-state attachment rules as `task update`.

## Delete

```bash
heliox task delete <id-or-key> --yes --json
```

Prefer closing (`--status done|cancelled`); delete only when deletion is the requested outcome.

## Task lifecycle (the common shape)

```bash
heliox task show HEL-14                             # read the task + comments first
heliox task update HEL-14 --status in_progress --json
# ... do the work ...
heliox task done HEL-14 --comment "<what was done, with evidence>" --json
```

After a failed mutation, re-run `task show` before reporting state.
