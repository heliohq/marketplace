# Acuity Scheduling (`heliox tool acuity -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Acuity is a
**flat provider** (not grouped like `google`): everything after `--` is the
acuity tool's own CLI.

```bash
heliox tool acuity [--account <key>] -- <resource> <verb> [flags...]
```

You are working the calendar of a business that takes client bookings on
Acuity — reading the schedule, booking / rescheduling / canceling
appointments, checking open slots, and looking up clients. Commands are
grouped by resource: `appointment`, `availability`, `type`, `calendar`,
`client`, `form`, `label`, `block`, plus top-level `me`. Every command prints
the provider's JSON verbatim.

## The mental model (read this first — it prevents the #1 footgun)

Booking is **id-driven, not name-driven**. Before you can book you almost
always need two ids, and you resolve them yourself:

- **appointment type id** — `type list` maps type names → ids **and durations**.
- **calendar id** — `calendar list` maps staff/calendar names → ids.

Then check what is actually open before proposing a time:

- `availability dates --type-id <id> --month YYYY-MM` → which days have slots.
- `availability times --type-id <id> --date YYYY-MM-DD` → the bookable slots on
  a day.

Only then `appointment create`. Proposing a time you did not pull from
`availability times` risks a validation rejection (the slot is taken or outside
the type's availability).

## Core commands

### Read the schedule

```bash
# list active appointments in a window (all filters optional)
heliox tool acuity -- appointment list --min-date 2026-07-01 --max-date 2026-07-31 --json
heliox tool acuity -- appointment list --email jane@example.com --json
heliox tool acuity -- appointment list --canceled --json     # canceled ones instead of active
heliox tool acuity -- appointment get <id> --json
```

`appointment list` is capped by `--max` (Acuity default 100) and ordered by
`--direction ASC|DESC`; there is no cursor — narrow with the date window
(`--min-date`/`--max-date`) and filters (`--calendar-id`, `--type-id`,
`--email`, `--first-name`, `--last-name`). Pass `--exclude-forms` to drop
intake-form payloads and speed up a large read.

### Find open slots

```bash
heliox tool acuity -- availability dates --type-id 88 --month 2026-07 --json
heliox tool acuity -- availability times --type-id 88 --date 2026-07-15 --json
# optional: --calendar-id to a specific staff calendar, --timezone America/New_York
```

### Book, edit, reschedule, cancel

```bash
# book (client-validated by default: honors availability + required fields)
heliox tool acuity -- appointment create \
  --type-id 88 --datetime 2026-07-15T09:00:00-0400 \
  --first-name Jane --last-name Doe --email jane@example.com --json

# admin booking: bypass availability/attribute validation, allow notes; REQUIRES --calendar-id
heliox tool acuity -- appointment create --type-id 88 --datetime "2026-07-15 9am" \
  --first-name Jane --last-name Doe --calendar-id 55 --notes "VIP" --admin --json

# edit client details / intake answers on an existing appointment
heliox tool acuity -- appointment update <id> --email new@example.com --field 3=Updated --json

# move to a new time / cancel
heliox tool acuity -- appointment reschedule <id> --datetime 2026-07-16T10:00:00-0400 --json
heliox tool acuity -- appointment cancel <id> --note "client asked to cancel" --json
```

`--datetime` is passed through verbatim; Acuity parses it with strtotime in the
business/calendar timezone. **ISO-8601 with an explicit offset**
(`2026-07-15T09:00:00-0400`) is the safe form — a bare `"9am"` is interpreted
in the business timezone, which may not be yours. Add `--no-email` to any
create/update/reschedule/cancel to suppress the client's confirmation email/SMS.

### Intake fields, clients, blocks, lookups

```bash
# intake form field ids (needed for --field id=value on create/update)
heliox tool acuity -- form list --json

# clients — update/delete are keyed on the client's NAME, not an id
heliox tool acuity -- client list --search jane --json
heliox tool acuity -- client create --first-name Jane --last-name Doe --email jane@example.com --json
heliox tool acuity -- client update --first-name Jane --last-name Doe --notes "prefers mornings" --json
heliox tool acuity -- client delete --first-name Jane --last-name Doe --phone 555-1234 --json

# block off time (start/end passed like --datetime)
heliox tool acuity -- block list --min-date 2026-07-01 --json
heliox tool acuity -- block create --start 2026-07-18T13:00:00-0400 --end 2026-07-18T17:00:00-0400 --calendar-id 55 --json
heliox tool acuity -- block delete <id> --json

# account identity + settings (business name, email, timezone, scheduling page)
heliox tool acuity -- me --json
```

Run `-- <resource> --help` (or `-- <resource> <verb> --help`) for the exact
flags rather than guessing.

## Footguns (where agents go wrong)

- **Resolve ids first.** `--type-id` and `--calendar-id` are numeric ids, not
  names. Run `type list` / `calendar list` and use the ids; never pass a name.
- **Propose only slots you pulled from `availability times`.** A client-mode
  `appointment create` for an unavailable time is rejected. If you must force a
  time (e.g. a phone booking), use `--admin` — but `--admin` **requires
  `--calendar-id`** and skips availability checks entirely.
- **`--notes` only lands on admin bookings.** On a client-mode create the notes
  field is ignored by Acuity; add `--admin --calendar-id <id>` to set notes.
- **Intake answers need field ids.** `--field id=value` takes the numeric field
  id from `form list` (repeatable). `--field name=value` will fail — the id
  must be an integer.
- **Client update/delete key on the name**, not an id: `--first-name` +
  `--last-name` identify the client (add `--phone` to disambiguate duplicates).
  There is no client-id lookup path in this tool.
- **Reschedule vs. update.** `reschedule` changes the *time* (`--datetime`);
  `update` changes client details / intake fields. Editing `--datetime` via
  `update` does nothing — use `reschedule`.
- **Cancel note flag is `--note`** (sent as Acuity's `cancelNote`); it is the
  message the client sees on the cancellation notification.
- **Tokens do not expire, so a revoked connection only shows up as a 401** on
  the next call. On `401 reconnect required`, relay a fresh
  `heliox tool acuity auth` link — do not retry the same token.

## Safety

- Booking, rescheduling, canceling, and blocking time all notify real clients
  by default. These are outward-facing actions — follow the sensitive-operation
  rule in [../SKILL.md](../SKILL.md), and prefer `--no-email` while you are
  still confirming details with the user.
- `client delete` is irreversible and cascades in Acuity; confirm the exact
  client (name + phone) with the user before running it.
