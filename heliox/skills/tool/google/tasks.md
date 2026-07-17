# Google Tasks (`heliox tool google tasks -- ...`)

Read [google.md](./google.md) for auth and account selection. Everything after
`--` is the tasks tool's own CLI. This tool writes the user's **personal Google
Tasks** — the lists that show up in their Gmail sidebar, Google Calendar, and
the Google Tasks mobile app. It is **not** the Helio workspace task system.

## Which task container? (read this first)

There are two unrelated task systems:

- **Helio tasks** — workspace/org collaboration objects (assignable, stateful).
  Use Helio's native task capabilities, **not** this tool.
- **Google Tasks** — the user's *private* Google account to-dos. This tool.

Default a casual "add a todo" to whichever container the user names. If it is
ambiguous, ask one short question. **Never write to both** — no silent
dual-write.

## Core commands

```bash
# Zero-friction quick capture → lands in the primary list (@default)
heliox tool google tasks -- create --title 'Email the vendor invoice'

# Read / filter (no text search — the Tasks API has no query language; read with --json)
heliox tool google tasks -- list --json                         # @default list
heliox tool google tasks -- list --list <list-id> --due-before 2026-07-31 --json
heliox tool google tasks -- get <task-id> --json
heliox tool google tasks -- lists list                          # all task lists

# Complete / reopen (reversible; multiple ids patched serially)
heliox tool google tasks -- complete <task-id>...
heliox tool google tasks -- reopen <task-id>...

# Edit / organize (reversible)
heliox tool google tasks -- update <task-id> --title '...' --due 2026-07-20
heliox tool google tasks -- update <task-id> --clear-due
heliox tool google tasks -- move <task-id> --to-list <other-list-id>
heliox tool google tasks -- clear                               # hide completed (reversible!)

# Lists
heliox tool google tasks -- lists create --title 'Trip planning'
heliox tool google tasks -- lists update <list-id> --title '...'
```

Check `-- --help` (or `-- <cmd> --help`) rather than guessing flags. `--list`
defaults to `@default` (the user's primary list), so simple todos need no list
argument.

## Behavior contract

- **Quick capture is zero-friction** — `create` / `complete` / `update` are
  low-risk daily actions; do **not** ask for confirmation. Over-confirming
  kills the value of "just jot it down."
- **Due is a date, not a time.** The API keeps only the date part of `--due`
  and drops the time. If the user asks for a specific time ("remind me tomorrow
  at 3pm"), **say so explicitly** — "Google Tasks only stores a date; for a
  timed reminder you'd want a calendar event" — and do not silently downgrade
  3pm into an all-day task. `--json` echoes what actually landed, so you can
  confirm the stored value.
- **Clean up done work with `clear`, not `delete`.** `clear` hides completed
  tasks and is reversible (`list --show-hidden` re-reveals them). Prefer it over
  bulk deletion for "clear out what I've finished."

## Deletion gradient (confirm first)

`delete` and `lists delete` are **irreversible** — there is no undo and no
undelete path in this tool.

- **`delete <task-id>...`** — recite the task titles and count, then confirm
  before running.
- **Assigned tasks** (tasks that came from Google Docs / Chat — `assignmentInfo`
  is non-empty in `list --json`, and the human view marks them `(assigned)`):
  deleting one **also deletes the original in Docs / Chat**. Default to **not**
  deleting these; instead point the user to the source doc/space to unassign. If
  they still want it gone, recite the cascade consequence first.
- **`lists delete <list-id>`** — deletes the whole list *and every task in it*
  (including any assigned-task originals). The most destructive action here:
  recite the list name + how many tasks it holds before running.

## Failure notes

- **Counting / finding a task**: completed tasks ticked off in a first-party
  client become *hidden* — if `--show-completed` doesn't show them, add
  `--show-hidden`. There is no text search: to find "that todo about X," run
  `list --json` and read the results yourself.
- **`move` across lists**: a repeating task cannot move to another list — the
  API returns a 400, passed through verbatim. That is a Google constraint, not
  a tool bug.
- **403 with a scope hint** → the connection predates the needed scope; ask the
  user to disconnect and reconnect (fresh consent re-grants everything). A 401
  reconnect-required means the refresh token was revoked or the password
  changed — same reconnect path.
- **Scale limits**: up to 2000 lists per user, 2000 subtasks per task; `list`
  returns at most 100 per page — paginate with `--page-token` when you need all
  of them.
