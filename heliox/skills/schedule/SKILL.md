---
name: schedule
description: "Use `heliox schedule ...` for durable user-visible future work: reminders, one-shot follow-ups, recurring briefs/check-ins, calendar-like events, and schedules the user must be able to list, update, disable, or delete. Trigger whenever the user says remind me, check later, every day/week, morning brief, follow up at a time, or asks to manage scheduled work. Do NOT use session-native cron / wakeup / sleep-loop tools for any user-visible deferred work — those run only inside the current session and the user cannot see, list, cancel, or observe them; `heliox schedule` lives in schedule-service and survives pod restarts, which is what users expect when they say 'remind me'."
user-invocable: false
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox schedule --help"
---

# Heliox Schedule

Start by reading `../shared/SKILL.md`.

Use Helio schedules for user-visible future work. They live in schedule-service and survive pod restarts.

Do not use session-native cron or wakeup tools for user-visible Helio work. The user cannot see, cancel, or observe those reliably.

## Server-derived type

The server derives `type` from the **shape of the persisted row** — there is no `--type` flag. Rule:

| Persisted shape | Type |
| --- | --- |
| `end_at` set OR `attendees` non-empty | `calendar` |
| `recurrence_cron` non-empty (and not calendar) | `cron` |
| neither | `one-shot` |

`cron + end_at` → `calendar` (a recurring calendar event: cron fires, `end_at` defines the slot length). `cron + start_at` alone is still `cron`.

The same rule applies on update — pass `--cron ""` on a cron row to demote it back to `one-shot`/`calendar` based on what other fields remain.

## Create

```bash
heliox schedule create "<name>" --start "<rfc3339>" --channel '#engineering' -d "<message body>" --json
heliox schedule create "<name>" --cron "<five-field-cron>" --channel '#engineering' -d "<message body>" --json
heliox schedule create "<name>" --start "<rfc3339>" --end "<rfc3339>" --channel '#engineering' --location "<text>" --attendees "@alice,@bob" --json
heliox schedule create "<name>" --cron "0 9 * * *" --channel '#engineering' -d "morning brief" --enable false --json
heliox schedule create "<name>" --start "<rfc3339>" -d "with files" -a /tmp/notes.md -a /tmp/chart.png --json
```

Flags:

- `-d, --description <text>` — required by the server on `cron`/`one-shot` rows (it's the message body posted into `--channel` when the schedule fires). Optional on `calendar` rows (the title suffices).
- `--start <RFC3339>` — fire time. Required for `one-shot` and `calendar`.
- `--end <RFC3339>` — closing time. Setting `--end` promotes the row to `calendar`.
- `--cron "<five-field>"` — recurring expression. Setting `--cron` auto-stamps the CLI process's local IANA timezone server-side (there is no `--tz` flag on `create`). Run the CLI in the user's timezone if cron timing matters; if the resolved zone is wrong, repair it post-create via `heliox schedule update --tz`.
- `--location "<text>"` — calendar location (Zoom link, room name).
- `--channel '#<name>'` — where the AI's reply lands when the schedule fires. Requires the `#` sigil. **Required** for `calendar` rows; optional for `cron`/`one-shot` (when omitted, the row fires into the owner's self-internal stream).
- `--attendees "@alice,@bob"` — comma-separated `@handle` list; requires the `@` sigil per attendee. Setting attendees promotes the row to `calendar`.
- `-a, --attachment <path>` — local file to upload and attach. Repeat for multiple files; order matches the user's flag order. Uploads happen **before** the POST, so a failed upload aborts the create.
- `--enable true|false` — create in the disabled state (`--enable false`). Defaults to enabled when the flag is omitted.

## List, show, delete

```bash
heliox schedule list --json
heliox schedule list --enabled true --json
heliox schedule list --enabled false --json
heliox schedule list --type cron --limit 100 --json
heliox schedule list --type one-shot --limit 20 --json
heliox schedule show <id> --json
heliox schedule delete <id> --yes --json
```

- `--enabled` is a string filter (`true` / `false`), not a boolean flag.
- `--type` is applied **client-side** after the SDK call against the same `cron|one-shot|calendar` enum the server emits. The CLI pulls ~5× the user-requested `--limit` (capped at 200) so type filtering returns a representative page.
- `--limit` defaults to 10. Use a higher explicit limit such as `--limit 100` before deciding a recurring job does not exist, especially in workspaces with many schedules.
- `schedule delete` **requires** `--yes` as a non-interactive ack token (no `--force` / interactive prompt).
- `schedule show` prints every field the SDK exposes (description, end, location, role, organizer, attendees, attachments, audit timestamps).

## Update

```bash
heliox schedule update <id> --name "<name>" --json
heliox schedule update <id> -d "<new description>" --json
heliox schedule update <id> --start "<rfc3339>" --json
heliox schedule update <id> --end "<rfc3339>" --json
heliox schedule update <id> --cron "<five-field-cron>" --json
heliox schedule update <id> --tz "<iana_timezone>" --json
heliox schedule update <id> --location "<text>" --json
heliox schedule update <id> --channel '#<name>' --json
heliox schedule update <id> --attendees "@alice,@bob" --json
heliox schedule update <id> -a /tmp/notes.md -a /tmp/chart.png --json
heliox schedule update <id> --enable true --json
heliox schedule update <id> --enable false --json
```

Clear flags (drop a previously set field; each is mutually exclusive with the matching value flag):

```bash
heliox schedule update <id> --clear-end --json           # calendar → one-shot/cron (drops end_at)
heliox schedule update <id> --cron "" --json             # cron → one-shot/calendar (drops recurrence_cron)
heliox schedule update <id> --clear-channel --json       # drop delivery target (rejected on calendar — see below)
heliox schedule update <id> --clear-attendees --json     # drop the entire attendee roster
heliox schedule update <id> --clear-attachments --json   # drop every attachment
```

Semantics worth knowing:

- **Type re-derives after the merge.** The server applies your patch, then re-runs the same shape rule from the Create section. `--cron ""` on a cron row demotes it to `one-shot` (or `calendar` if `end`/`attendees` remain). Adding `--cron` on a one-shot promotes it to `cron`. You do not need to (and cannot) pass `--type`.
- **`--clear-channel` works on every schedule type** (post calendar-notif-unify). Without a channel, fires publish only into the owner's `notifications.{org}.{owner}` stream and the card lacks a pivot target (the assistant can't auto-respond in a channel because none is set). If you want a calendar row to fire into a channel, keep `--channel` populated.
- **`--description`** on `calendar` rows: passing `-d ""` clears the description. On `cron`/`one-shot` the server rejects an empty description (the body is mandatory).
- **`--enable false`** is the preferred "park it for later" verb. Use it instead of `delete` when the user may want the schedule back.
- **Attachments replace.** `-a/--attachment` replaces the roster with the new list (uploads happen before the PATCH, same as create). To delete every attachment without replacement use `--clear-attachments`.
- **Mutex pairs** (the CLI rejects these combinations at parse time, before hitting the server):
  - `--end` ⨯ `--clear-end`
  - `--channel` ⨯ `--clear-channel`
  - `--attendees` ⨯ `--clear-attendees`
  - `--attachment` ⨯ `--clear-attachments`
