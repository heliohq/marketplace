# Calendly (`heliox tool calendly -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Calendly is a
**flat provider**: everything after `--` is the Calendly tool's own CLI,
speaking the Calendly REST API (and the 2026 Scheduling API) with the
connected account's OAuth token.

```bash
heliox tool calendly [--account <key>] -- <group> <verb> [flags...]
```

Use it to answer "when am I free / what's on my Calendly", share the right
booking link (including single-use links), see who booked and their answers,
cancel a meeting, mark no-shows, and (on paid plans) book a slot directly.
It reads and acts on the user's existing Calendly setup; it does **not** manage
event-type configuration, webhooks, or org administration.

## Two things to learn once: URIs and `me`

Calendly identifies every resource by a **full URI**, not a bare id, e.g.
`https://api.calendly.com/users/AAAA`, `.../event_types/BBBB`. Every flag that
takes a resource accepts **either** the full URI **or** the bare UUID (the tool
expands it). Start with `me` to get your own URIs:

```bash
heliox tool calendly -- me      # your user URI, organization URI, scheduling_url, timezone
```

Wherever a `--user` is expected you can pass the literal `me` (the default),
a bare UUID, or a full user URI. `--org` switches a listing to your whole
organization instead of just you.

## Command surface

```bash
# Event types (bookable meeting kinds + their scheduling_url to share)
heliox tool calendly -- event-type list [--user me|<uri>] [--org] [--count N] [--page-token T]
heliox tool calendly -- event-type get <id|uri>

# Availability
heliox tool calendly -- availability slots --event-type <id|uri> --from <ISO> --to <ISO>
heliox tool calendly -- availability busy [--user me|<uri>] --from <ISO> --to <ISO>
heliox tool calendly -- availability schedule list [--user me|<uri>]

# Booked meetings
heliox tool calendly -- event list [--user me|<uri>] [--org] [--status active|canceled] \
    [--invitee-email e] [--from ISO] [--to ISO] [--count N] [--page-token T]
heliox tool calendly -- event get <id|uri>
heliox tool calendly -- event invitees <id|uri> [--status active|canceled] [--email e]
heliox tool calendly -- event cancel <id|uri> [--reason "..."]

# No-shows (the invitee arg for marking is the FULL invitee URI from `event invitees`)
heliox tool calendly -- invitee no-show <invitee-uri>
heliox tool calendly -- invitee no-show <no-show-id|uri> --undo

# Share a single-use booking link
heliox tool calendly -- link create --event-type <id|uri>

# Book directly on an invitee's behalf (Scheduling API: paid plans only)
heliox tool calendly -- book create --event-type <id|uri> --start <UTC ISO> \
    --name "..." --email e --timezone America/New_York \
    [--location-kind k] [--location v] [--guest e]...

# Resolve teammates' user URIs (for availability/busy on colleagues)
heliox tool calendly -- org members [--email filter]
```

Run any `-- <group> <verb> --help` for the full flag list. List verbs paginate
with `--count` + `--page-token` (the cursor is `pagination.next_page`'s
`page_token` in the previous response).

## Rules that bite

- **There is no reschedule endpoint.** To reschedule, either send the invitee
  their `reschedule_url` (returned by `event invitees`) or cancel and share a
  new booking link. Do not look for a `reschedule` verb.
- **Availability ranges are capped.** `availability slots`
  (`event_type_available_times`) accepts at most **~1 week** per request: the
  API reference caps it at 1 week even though a Calendly guide page says 31
  days, and the live API validates. `availability busy` is **≤ 7 days**. For a
  longer window, **chunk it into ≤ ~1-week calls** yourself; the tool passes
  your range straight through and never trims it, so an over-long range comes
  back as a Calendly validation error, not a silent clamp. Slot windows must be
  in the future.
- **`book create` requires a paid Calendly plan.** On a free-tier account
  Calendly returns 403; the tool surfaces that verbatim. Do not treat it as a
  tool failure: relay that direct booking needs a paid plan, and fall back to
  `link create` (share a booking link) instead.
- **Marking a no-show needs the full invitee URI** (`.../scheduled_events/{uuid}/invitees/{uuid}`
  from `event invitees`), not a bare UUID: a bare UUID is ambiguous and the
  tool rejects it. `--undo` instead takes the no-show's own id/URI.

## Safety

Cancelling a meeting, marking a no-show, minting a booking link, and booking on
someone's behalf are outward-facing actions (they notify invitees or create
shareable links). Follow the sensitive-operation rule in `../SKILL.md`:
confirm with the user before cancelling a real meeting or booking on an
invitee's behalf.
