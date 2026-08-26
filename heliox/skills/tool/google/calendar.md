# Google Calendar (`heliox tool google calendar -- ...`)

Read [google.md](./google.md) first for auth and account selection. Everything
after `--` is the calendar tool's own CLI. All time arguments are **RFC3339 with
an explicit offset** (`2026-07-16T14:00:00-07:00`), never a bare clock time.
Connecting Gmail does **not** connect Calendar: each Google app is its own
connection with its own consent. If a Calendar command reports no connection,
run `heliox tool google auth calendar` and forward the link to the user.

## Core commands

```bash
# Discover calendars first: ids, time zones, and access roles come from here
heliox tool google calendar -- calendars list --json

# Today / this week's schedule (expand recurring events, sort by start)
heliox tool google calendar -- events list --from 2026-07-16T00:00:00-07:00 --to 2026-07-17T00:00:00-07:00 \
  --single-events --order-by startTime --json

# Search the user's own events by full text
heliox tool google calendar -- events list --query "roadmap review" --single-events --json

# Find a free slot: query FREE/BUSY, never read someone else's events
heliox tool google calendar -- freebusy --calendar primary,alice@example.com \
  --from 2026-07-16T09:00:00-07:00 --to 2026-07-16T18:00:00-07:00 --json

# Create a meeting with a Google Meet link and invite guests
heliox tool google calendar -- events create --summary "Design sync" \
  --from 2026-07-17T10:00:00-07:00 --to 2026-07-17T10:30:00-07:00 \
  --attendee alice@example.com --attendee bob@example.com --meet --json

# Reschedule (patch: only the fields you pass change; the rest is untouched)
heliox tool google calendar -- events update <event-id> \
  --from 2026-07-17T11:00:00-07:00 --to 2026-07-17T11:30:00-07:00

# RSVP as yourself (the organizer is always notified)
heliox tool google calendar -- events respond <event-id> --status accepted
```

Also available: `calendars get`, `events get`, `events instances`,
`events delete`. Check `-- --help` rather than guessing flags.

## Reaching other people: the approval gate handles it

`events create` / `events update` with `--attendee` are policy-gated: instead
of running, heliox exits with `APPROVAL_REQUIRED` and prints the exact
request/replay commands. Follow that output (full flow in the tool skill's
"Approval gate" section). `--send-updates none` does not exempt: the event
still lands on attendees' calendars, so a "quiet" invite is still an invite.
The approval card **is** the human check. Do not also pre-confirm in chat.

Everything else is routine. Run it without extra confirmation: purely
personal events (no attendees), rescheduling or cancelling an existing meeting
without touching the attendee list, and `respond`. Existing attendees get the
normal update/cancellation notices; that is expected collaboration ripple, not
a new reach. Still avoid `--send-updates none` on routine edits: silent
changes leave guests with stale invites.

## Recurring events: edit the right level

- To change **one occurrence** (e.g. "move next Tuesday's standup"), first run
  `events instances <event-id>` to get that occurrence's own id, then
  `events update <instance-id>`.
- To change **the whole series**, update the base recurring event's id.
- Editing the wrong level is the most common calendar mistake; check with
  `instances` before touching a single occurrence.

## Time zones

- A calendar's time zone comes from `calendars list` / `calendars get`
  (`tz=...`). When reporting times to a user or across attendees in different
  zones, state the explicit offset, never a naked clock time.

## Failure notes

- **No connection / connected Gmail but not Calendar** → auth fails; run
  `heliox tool google auth calendar`, forward the link, and remind the user
  that Gmail's authorization does not cover Calendar.
- **Multiple Google accounts** → pass `--account <email>` before `--` to pick
  which connection to use.
- **403 with a scope hint** → the connection predates a needed scope; ask the
  user to disconnect and reconnect (fresh consent re-grants everything).
- **freebusy on a calendar you can't see** → the response carries a per-calendar
  `error` entry (not a top-level failure); tell the user that owner needs to
  share their free/busy.
- **Counting events** → `events list` paginates with `--page-token`; there is no
  cheap estimate field, so page to the end to count.
