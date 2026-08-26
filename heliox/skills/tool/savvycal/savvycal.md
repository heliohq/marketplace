# SavvyCal (`heliox tool savvycal -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. SavvyCal is a
**flat provider** (not grouped like `google`): everything after `--` is the
savvycal tool's own CLI.

```bash
heliox tool savvycal [--account <key>] -- <resource> <verb> [flags...]
```

SavvyCal is a scheduling-link product. Three resource groups:

- `me`: the connected account's identity.
- `event`: bookings made through SavvyCal (list / get / create / cancel).
- `link`: scheduling links (list / get / create / update / toggle /
  duplicate / delete) plus `link slots` for availability.

Every command prints the provider's JSON verbatim. List commands
(`event list`, `link list`) emit the full `{entries, metadata}` envelope; page
with the opaque cursors in `metadata` via `--after` / `--before`.

## Core commands

### Identity

```bash
heliox tool savvycal -- me --json
```

### Events

```bash
# default: confirmed + upcoming. Widen with --state / --period.
heliox tool savvycal -- event list --state all --period all --limit 50 --json
heliox tool savvycal -- event list --after <cursor> --json      # next page
heliox tool savvycal -- event get <event_id> --json
heliox tool savvycal -- event cancel <event_id> --reason "Rescheduling" --json
```

`--state` = `confirmed|canceled|all` (default `confirmed`); `--period` =
`past|upcoming|all` (default `upcoming`); `--limit` max 100.

### Scheduling links

```bash
heliox tool savvycal -- link list --json
heliox tool savvycal -- link get <link_id> --json

# create a personal link, or a team/individual-scope link with --scope <slug>
heliox tool savvycal -- link create --name "Intro Call" --type single --json
heliox tool savvycal -- link create --name "Team Sync" --scope acme-inc --json

heliox tool savvycal -- link update <link_id> --description "Updated" --json
heliox tool savvycal -- link toggle <link_id> --json      # active <-> disabled
heliox tool savvycal -- link duplicate <link_id> --json
heliox tool savvycal -- link delete <link_id> --json
```

`--type` = `recurring` (multi-use, default) or `single` (single-use).

## Booking a time (read this before `event create`)

`event create` **fails unless `--start`/`--end` match an available slot** on the
link. Always call `link slots` first, then book a real slot:

```bash
# 1. find available times (defaults: from now, until +7 days; override with --from/--until)
heliox tool savvycal -- link slots <link_id> --from 2026-08-01T00:00:00Z --until 2026-08-08T00:00:00Z --json

# 2. book one, echoing an exact slot's start_at/end_at + the scheduler's details
heliox tool savvycal -- event create <link_id> \
  --display-name "Bob Jones" --email bob@acme.co \
  --start 2026-08-01T10:00:00Z --end 2026-08-01T10:30:00Z \
  --time-zone America/New_York \
  --field q1=answer --metadata '{"source":"helio"}' --json
```

Notes:

- Each slot carries a **cumulative `rank`**. To offer non-overlapping options,
  filter to one rank (`rank === N`), not `rank <= N`.
- `--field id=value` (repeatable) answers a link's booking-form questions;
  `--metadata` is a raw JSON object passed through.
- Conferencing info (e.g. a Zoom link) may attach a moment after creation:
  re-`event get` if it's missing from the create response.

## Errors

- A `422` returns SavvyCal's `{"errors": {...}}` validation body verbatim (bad
  slot, missing field). Read it and fix the inputs; don't retry blindly.
- `401 reconnect required` → relay a fresh `savvycal auth` link (see ../SKILL.md).

## Safety

Creating and cancelling events acts on the user's real calendar and notifies
the other party. Treat `event create` and `event cancel` as outward-facing
actions: confirm the person, time, and link with the user before you book or
cancel on their behalf (per the sensitive-operation rule in `../SKILL.md`).
