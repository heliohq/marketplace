---
name: task
description: "Use `heliox task ...` for Helio task lifecycle: creating, listing, showing, updating status, assigning, commenting on, attaching files to, or deleting tasks. Trigger whenever a task number, task card, task assignment, status transition, or task comment is part of the job."
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

- Tasks are org-scoped and identified by task number.
- `task create` requires `--channel-id`; that channel is the task's routing key.
- Task channel assignment is immutable after create. `task update` cannot change or clear channel.
- Always pass `--json` for assistant-facing task operations so Helio can render structured task cards.

## Commands

### List

```bash
heliox task list [--status todo|in_progress|in_review|done] [--assignee-id <user_id>] [--channel-id <channel_id>] --json
```

### Create

```bash
heliox task create "<title>" --channel-id <channel_id> [--description "<text>"] [--assignee-id <user_id>] [--status todo|in_progress|in_review|done] --json
```

Pass the title explicitly. Do not rely on interactive prompts.

### Show

```bash
heliox task show <number> --json
```

### Update

```bash
heliox task update <number> [--title "<title>"] [--description "<text>" | --clear-description] [--assignee-id <user_id> | --unassign] [--status todo|in_progress|in_review|done] --json
```

`task update` requires at least one update flag. Do not combine:

- `--description` with `--clear-description`
- `--assignee-id` with `--unassign`

### Assign or unassign

```bash
heliox task update <number> --assignee-id <user_id> --json
heliox task update <number> --unassign --json
```

Assignment is part of `task update`. There is no separate assignment command.

### Comments

```bash
heliox task comments list <number> --json
heliox task comments add <number> "<body>" --json
heliox task comments add <number> "<body>" --reply-to <comment_id> --json
heliox task comments add <number> --file ./trace.txt --file ./screenshot.png --json
heliox task comments update <number> <comment_id> "<body>" --json
heliox task comments delete <number> <comment_id> --yes --json
```

Use task comments for durable task evidence. Use channel messages for
conversation. `task comments add` accepts repeated `--file` flags through the
same attachment upload path as `channel send`; attachment-only comments are
valid when at least one file is provided.

### Delete

```bash
heliox task delete <number> --yes --json
```

Prefer status updates (`done` or `in_review`) over deletes. Delete only when deletion is the actual requested outcome.

## Recommended execution path

For an existing task:

1. `heliox task show <number> --json`
2. `heliox task comments list <number> --json`
3. `heliox task update <number> --status in_progress --json`
4. Do the work.
5. `heliox task comments add <number> "<evidence>" --json`
6. `heliox task update <number> --status in_review --json`
7. `heliox task show <number> --json`

## Failure handling

- If a task number is not found, list tasks with the likely channel filter: `heliox task list --channel-id <channel_id> --json`.
- If `task update` rejects flags, remove the conflicting pair and retry.
- After a failed mutation, do not narrate success. Re-run `task show` first.

## Ready patterns

```bash
heliox task show 14 --json
heliox task comments list 14 --json
heliox task update 14 --status in_progress --json
heliox task comments add 14 "Implemented the change and verified the result." --json
heliox task update 14 --status in_review --json
heliox task show 14 --json
```

```bash
heliox task create "Fix login redirect" --description "Repro, root cause, and expected behavior." --channel-id "$CHANNEL_ID" --assignee-id "$USER_ID" --status todo --json
```
