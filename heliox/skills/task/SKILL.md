---
name: task
description: "Use `heliox task ...` for Helio task lifecycle: creating, listing, showing, updating status, assigning, commenting on, or deleting tasks. Trigger whenever a task number, task card, task assignment, status transition, or task comment is part of the job."
user-invocable: false
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox task --help"
---

# Heliox Task

Start by reading `../shared/SKILL.md`.

Use this skill whenever task state is part of the job.

## Current model

- Tasks are org-scoped and identified by a 24-hex ObjectID or a `PREFIX-NUMBER` key.
- `task create` requires `--channel`; that channel is the task's routing key.
- The task's channel is immutable after create. `task update` cannot change or clear it.
- Always pass `--json` for assistant-facing task operations so Helio can render structured task cards.
- Status enum: `open | in_progress | blocked | done | cancelled`. `blocked` means "stuck, still needs attention" — NOT closed.
- Priority enum: `low | normal | high | urgent`. Optional; absent = "no priority set."
- Deadlines are RFC3339 timestamps (`2026-05-20T17:00:00Z`). Stored UTC server-side.
- Labels are freeform short strings; passed as a comma-separated list on the CLI.

## Commands

### List

```bash
heliox task list --json
heliox task list --status in_progress --json
heliox task list --assignee @alice --json
heliox task list --assignees "@alice,@bob" --json
heliox task list --channel '#engineering' --json
```

`--assignee` / `--assignees` require the `@` sigil; `--channel` requires `#`. 24-hex ids are rejected.

### Create

```bash
heliox task create "<title>" --channel '#engineering' --json
heliox task create "<title>" --channel '#engineering' --assignee @alice --status in_progress --json
heliox task create "<title>" --channel '#engineering' -d "<plain-text body>" --priority high --json
heliox task create "<title>" --channel '#engineering' --deadline 2026-05-20T17:00:00Z --labels frontend,perf --json
```

The title is the positional arg. Supported flags: `--channel` (required), `--assignee`, `--status`, `-d/--description`, `--priority`, `--deadline`, `--labels`, `-a/--attachment`.

Description: `-d/--description "text"` accepts plain text; newlines split into paragraphs. The wire is a Tiptap doc (the CLI wraps your text) — you do NOT pass JSON. Use task comments for ongoing context after creation.

Task key prefix is server-assigned from workspace defaults.

Attach files at create time with `-a/--attachment` (repeatable):

```bash
heliox task create "Repro: API 500" --channel '#engineering' -a ./repro.log --json
heliox task create "Visual bug" --channel '#engineering' -a ./shot1.png -a ./shot2.png --json
```

Image refs become inline image nodes in the task description (`![name](helio://attachment/...)`); non-image refs ride the `attachments[]` sidecar. Both surface in the JSON response under `attachments[].uri`; fetch the bytes via `heliox blob get helio://attachment/...` (see `heliox:shared` §Attachments).

When you also pass `-d`, text paragraphs land before the inline image nodes in the description.

### Show

```bash
heliox task show <id-or-key> --json
heliox task show <id-or-key> --activity --json   # inline the activity log (capped at last 20)
```

Accepts a 24-hex ObjectID or `PREFIX-NUMBER`. The JSON response includes:

- `task.description` — Tiptap doc; image nodes carry `attrs.src = "helio://attachment/<att_id>"`
- `task.attachments[]` — every ref with a populated `uri` field; the sidecar covers non-image refs too
- `comments[].attachments[]` — same shape; comment-side attachments carry `uri` likewise
- `activities[]` — only when `--activity` is passed; one row per status / assignee / priority / deadline / labels change

### Update

```bash
heliox task update <id-or-key> --title "<new title>" --json
heliox task update <id-or-key> --status in_progress --json
heliox task update <id-or-key> --status done --json
heliox task update <id-or-key> --assignee @alice --json
heliox task update <id-or-key> -d "<new plain-text body>" --json
heliox task update <id-or-key> --priority urgent --deadline 2026-06-01T09:30:00Z --json
heliox task update <id-or-key> --labels frontend,perf --json
heliox task update <id-or-key> -a ./new-shot.png --clear-attachments --json   # mutually exclusive — pick ONE
heliox task update <id-or-key> --clear-attachments --clear-description --json # remove image + its description
heliox task update <id-or-key> --clear-attachments -d "<new plain text>" --json # replace image with prose
```

Supported update flags: `--title`, `--status`, `--assignee`, `-d/--description`, `--priority`, `--deadline`, `--labels`, `-a/--attachment`, `--clear-attachments`, `--clear-description`. Every flag uses "empty preserves" semantics — passing an empty string / not passing the flag leaves the current value alone.

Attachment editing is tri-state:

- omit both flags → current attachment allowlist unchanged
- `-a file1 -a file2` → uploads new files and **replaces** the entire allowlist
- `--clear-attachments` → drops all existing attachments

The two attachment flags are mutually exclusive — the CLI rejects them together client-side before any upload.

**Any attachment-replacement requires a description decision.** Tasks created via `task create -a <file>` embed `helio://attachment/<id>` image refs inside the Tiptap description. Replacing or clearing the allowlist while leaving those refs in place would trip server-side validation (docs/design/102 AD-3). The CLI rejects **both** `--clear-attachments` and `-a/--attachment` unless paired with one of:

- `--clear-description` → drop the description too (the natural choice when the description's only content WAS the image)
- `-d "<new prose>"` → replace the description with something that doesn't reference the cleared attachments

This applies to non-image attachments (PDFs, etc.) too — the CLI doesn't know the MIME type until upload completes, so the rule is uniform. Pair `-a doc.pdf -d "<existing prose>"` if you want to keep the description, or `-a doc.pdf --clear-description` if not.

If you use `-d` to rewrite the description AND `-a` to change attachments, you are responsible for keeping the description's `helio://attachment/...` image references consistent with the new allowlist. Mismatches return 400 server-side (docs/design/102 AD-3).

`--assignee ""` (empty string) preserves the current assignee; pass a new `@handle` to reassign.

### Comments

```bash
heliox task comments list <task-id> --json
heliox task comments add <task-id> "<body>" --json
heliox task comments add <task-id> "<body>" --parent <comment_id> --json
heliox task comments update <task-id> <comment_id> "<new body>" --json
heliox task comments update <task-id> <comment_id> "<new body>" -a ./diff2.patch --json
heliox task comments update <task-id> <comment_id> "<new body>" --clear-attachments --json
heliox task comments delete <task-id> <comment_id> --yes --json
```

Use task comments for durable task evidence. Use channel messages for conversation. `--parent` is the reply-to comment id.

`task comments add` accepts `-a/--attachment` (repeatable). When `-a` is supplied, the body positional is optional — attachment-only comments are valid (matches channel-message semantics):

```bash
heliox task comments add <task-id> "see attached" -a ./diff.patch --json
heliox task comments add <task-id> -a ./repro.log --json          # attachment-only
heliox task comments add <task-id> -a ./one.png -a ./two.png --json
```

`task comments update` follows the same tri-state attachment rules as `task update`: omit attachment flags → leave allowlist alone; `-a file` → replace allowlist; `--clear-attachments` → drop all attachments. The two flags are mutually exclusive (client-side guard).

Each ref appears in the response's `comment.attachments[].uri` as `helio://attachment/<att_id>` — fetch via `heliox blob get` (see `heliox:shared` §Attachments).

### Delete

```bash
heliox task delete <id-or-key> --yes --json
```

Prefer status updates (`done` or `cancelled`) over deletes. Delete only when deletion is the actual requested outcome; `--yes` is required to confirm.

## Recommended execution path

For an existing task:

1. `heliox task show <id-or-key> --json`
2. `heliox task comments list <id-or-key> --json`
3. `heliox task update <id-or-key> --status in_progress --json`
4. Do the work.
5. `heliox task comments add <id-or-key> "<evidence>" --json`
6. `heliox task update <id-or-key> --status done --json`
7. `heliox task show <id-or-key> --json`

## Failure handling

- If a task id is not found, list tasks with the likely channel filter: `heliox task list --channel '#<name>' --json`.
- If the CLI rejects `--priority` or `--deadline` client-side, it's a value-shape error — priority must be one of `low|normal|high|urgent`, deadline must be RFC3339 (`2026-05-20T17:00:00Z`).
- After a failed mutation, do not narrate success. Re-run `task show` first.

## Ready patterns

```bash
heliox task show TASK-14 --json
heliox task comments list TASK-14 --json
heliox task update TASK-14 --status in_progress --json
heliox task comments add TASK-14 "Implemented the change and verified the result." --json
heliox task update TASK-14 --status done --json
heliox task show TASK-14 --json
```

```bash
heliox task create "Fix login redirect" --channel '#engineering' --assignee @alice --status open --json
```
