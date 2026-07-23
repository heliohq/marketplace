# Cal.com (`heliox tool calcom -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Cal.com is a
**flat provider** (not grouped like `google`): everything after `--` is the
calcom tool's own CLI.

```bash
heliox tool calcom [--account <key>] -- <resource> <verb> [flags...]
```

Use Cal.com as a **scheduling actuator**: inspect the meeting types a user
offers, find open time, and book / cancel / reschedule on their behalf, then
read the resulting bookings. Every subcommand supports `--json` and prints the
provider's `data` payload (the `{status,data}` envelope is already unwrapped).

## The mental model (read this first)

Booking a meeting is a two-step flow, and the two ids are different:

1. **`event-type`** — the bookable meeting *type* the user offers (e.g. "30-min
   intro"). List them to get an `eventTypeId` (an integer). This is the entry
   point: a booking needs an `eventTypeId`.
2. **`slot`** — open times for a given event type inside a bounded date range.
   Propose or confirm a slot's `start` before booking.
3. **`booking`** — a scheduled meeting, addressed by its **`bookingUid`** (a
   string, not the numeric event-type id). Read, create, cancel, reschedule.

Time is always explicit: every `booking create` / `reschedule` takes an ISO-8601
`--start` (send it in **UTC**), and `create` also takes the attendee's IANA
`--attendee-tz` (e.g. `America/New_York`). The tool never guesses a time zone.

## Core commands

### Discover what the user offers

```bash
heliox tool calcom -- event-type list --json                 # ids, slugs, lengths
heliox tool calcom -- event-type get --id <eventTypeId> --json
heliox tool calcom -- me --json                              # the connected Cal.com profile
```

### Find open time

```bash
# bounded range (keep it tight — a few days, not months)
heliox tool calcom -- slot list --event-type-id <id> \
  --start 2026-02-01T00:00:00Z --end 2026-02-08T00:00:00Z --json
```

### Read the calendar

```bash
heliox tool calcom -- booking list --json                    # all bookings
heliox tool calcom -- booking list --status upcoming --json  # upcoming|past|cancelled
heliox tool calcom -- booking get --uid <bookingUid> --json
```

### Book, cancel, reschedule

```bash
# create: eventTypeId + start + the three attendee fields are required
heliox tool calcom -- booking create \
  --event-type-id <id> --start 2026-02-03T09:00:00Z \
  --attendee-name "Ada Lovelace" --attendee-email ada@example.com \
  --attendee-tz America/New_York \
  [--notes "prep call"] [--metadata '{"source":"helio"}'] --json

heliox tool calcom -- booking cancel --uid <bookingUid> [--reason "conflict"] --json
heliox tool calcom -- booking reschedule --uid <bookingUid> \
  --start 2026-02-04T09:00:00Z [--reason "moved"] --json
```

### Availability schedules

```bash
heliox tool calcom -- schedule list --json                   # working-hours schedules
```

## Footguns

- **Two different ids.** `--event-type-id` is a numeric event-type id (from
  `event-type list`); `--uid` is a booking's string uid (from `booking list` /
  `booking get`). They are not interchangeable.
- **Send `--start` in UTC.** Cal.com interprets the booking start as sent; a
  local-time string without a UTC offset lands the meeting at the wrong hour.
  For `create`, the attendee's own `--attendee-tz` is separate from the UTC
  start.
- **Keep `slot list` ranges bounded.** Query a few days, not an open-ended span.
- **Errors are surfaced verbatim.** A non-2xx prints Cal.com's `status:error`
  body; exit 1 for API failures, exit 2 for usage/flag errors.
