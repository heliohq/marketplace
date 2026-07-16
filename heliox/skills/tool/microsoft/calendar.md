# Outlook Calendar (`heliox tool microsoft calendar -- ...`)

Read [microsoft.md](./microsoft.md) for auth and account selection. Everything
after `--` is the calendar tool's own CLI, a faithful projection of Microsoft
Graph `/me/events`, `/me/calendars`, and `/me/calendarView`. Time windows use
`--start` / `--end`; filtering passes OData through `--filter '<OData>'`.

## Core commands

```bash
# Read
heliox tool microsoft calendar -- calendars list --json
heliox tool microsoft calendar -- events list --start 2026-07-16 --end 2026-07-23 --max 50 --json   # window via /me/calendarView
heliox tool microsoft calendar -- events get <id> --json

# Own free/busy (v1): computed from YOUR calendar only — no reading of others' availability
heliox tool microsoft calendar -- freebusy --start 2026-07-16T09:00 --end 2026-07-16T18:00 --json

# Write (reversible)
heliox tool microsoft calendar -- events create --subject "Sync" --start 2026-07-16T15:00 --end 2026-07-16T15:30 \
    --attendees a@b.com --location "Room 4" --online
heliox tool microsoft calendar -- events update <id> --start 2026-07-16T16:00 --end 2026-07-16T16:30
heliox tool microsoft calendar -- events cancel <id> --comment "Rescheduling"   # notifies attendees

# Meeting-invite reply (notifies the organizer)
heliox tool microsoft calendar -- events respond <id> --action accept   # also decline | tentative; --comment, --no-notify
```

Check `-- --help` for full flags. Every command takes `--json`; lists default
to a human-readable table with `--page <token>` for explicit pagination.

## Confirm before you notify others

Creating, changing, or cancelling an event with attendees **sends a
notification to those people** — an outward-facing action. Follow the
sensitive-operation rule in `../shared/SKILL.md`:

- Before creating/updating/cancelling any event that has **attendees**, confirm
  the details with the user first — subject, time, and who gets invited/notified.
  Events with no attendees (your own blocks) are lower-stakes.
- When scheduling, check `freebusy` first, then `create` — do not blind-book
  over existing commitments.
- `respond` and `cancel` notify by default; use `--no-notify` only when the
  user explicitly wants a silent change.

## Failure notes

- No connection → `heliox tool microsoft auth calendar`, relay the link.
- 409 with account candidates → re-run with `--account <key>`.
- 403 scope hint / 401 reconnect required → disconnect and reconnect (fresh
  consent; `prompt=select_account` re-picks the account).
- **Others' availability is not available in v1.** `freebusy` reports only the
  signed-in user's own busy windows. Reading other attendees' free/busy
  (`findMeetingTimes` / `getSchedule`) needs a broader scope and is
  work/school-only — it is not connected. If the user asks to find a slot that
  works for other people, say that only their own calendar is visible.
- `delete` is intentionally not exposed — use `cancel` (notifies attendees, goes
  through the proper path).
