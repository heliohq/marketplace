# Outreach (`heliox tool outreach -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Outreach is a
**flat provider**: everything after `--` is the Outreach tool's own CLI,
speaking the Outreach API v2 (JSON:API) with the connected account's OAuth user
token.

```bash
heliox tool outreach [--account <key>] -- <resource> <verb> [flags...]
```

Resources: `prospect`, `account`, `sequence`, `enrollment`, `mailbox`,
`mailing`, `call`, `task`, `opportunity`, `user`, `template`, `stage`,
`persona`. Run `-- <resource> --help` for the full flag surface.

## Output shape (learn once, applies to every command)

Every resource comes back **flattened** — no JSON:API envelope to unwrap:

```json
{ "id": "123", "type": "prospect", "firstName": "Sally", "emails": ["s@x.com"],
  "account_id": "5", "owner_id": "9" }
```

Relationship ids are hoisted to `<name>_id` (e.g. `account_id`, `owner_id`,
`stage_id`). `list` commands return a page:

```json
{ "items": [ ... ], "next_cursor": "<opaque>", "count": 42 }
```

Paginate by passing `next_cursor` back as `--cursor`; page size is `--limit`.
`--count` adds the total `count`. `--sort <attr>` (prefix `-` for descending)
and `--fields a,b,c` (sparse fieldset) work on every `list`.

## The core loop: enroll a prospect in a sequence

This is Outreach's central write. Enrolling needs three ids — a prospect, a
sequence, and a **mailbox** (the seat that sends the cadence):

```bash
heliox tool outreach -- prospect list --q "sally"          # find the prospect id
heliox tool outreach -- sequence list --name "Cold Q3"     # find the sequence id
heliox tool outreach -- mailbox list                       # find the sending mailbox id
heliox tool outreach -- enrollment add --prospect-id 1 --sequence-id 2 --mailbox-id 3
```

`enrollment` is the human word for Outreach's `sequenceState`. Manage a live
enrollment with its state actions:

```bash
heliox tool outreach -- enrollment list --prospect-id 1    # who is in what
heliox tool outreach -- enrollment pause  <sequenceState-id>
heliox tool outreach -- enrollment resume <sequenceState-id>
heliox tool outreach -- enrollment finish <sequenceState-id>   # stop the cadence
```

## Prospects & accounts (the CRM objects)

```bash
heliox tool outreach -- prospect list --q "acme" --owner-id 9
heliox tool outreach -- prospect get 123
heliox tool outreach -- prospect create --email s@x.com --first-name Sally --account-id 5
heliox tool outreach -- prospect update 123 --title "VP Sales"
heliox tool outreach -- account list --q "acme" --domain acme.com
```

`--q` is Outreach's global full-text search and works **only** on `prospect`
and `account`. Elsewhere use the field filters the `--help` lists (`--email`,
`--account-id`, `--state`, ...). For any attribute without a dedicated flag,
use `--attr key=value` (repeatable; the value is parsed as JSON when valid, so
`--attr score=42` sends a number, `--attr tags='["a","b"]'` an array).

## Working the task queue

```bash
heliox tool outreach -- task list --owner-id 9 --state incomplete
heliox tool outreach -- task complete 9 --note "left voicemail"   # markComplete
heliox tool outreach -- task snooze 9 --param snoozeUntil=2026-08-01T00:00:00Z
heliox tool outreach -- task create --action call --due 2026-08-01T00:00:00Z --prospect-id 1
```

## Reporting reads

```bash
heliox tool outreach -- mailing list --prospect-id 1 --state opened   # email outcomes
heliox tool outreach -- call list --prospect-id 1
heliox tool outreach -- opportunity list
heliox tool outreach -- sequence steps 12                             # inspect a cadence
```

## Footguns

- **Ids are numeric** — every `get`/action takes a numeric id; a non-numeric
  arg fails before any request.
- **`enrollment add` needs a mailbox** connected to a real seat, or the enroll
  4xx's. List mailboxes first; do not guess the id.
- **Scopes are per-resource and not additive** — a `403` with
  `unauthorizedOauthScope` means the connection was granted without that
  resource's scope; reconnect to widen consent (this also invalidates the
  token, so heliox will prompt a reconnect).
- **Rate limit**: a `429` surfaces `X-RateLimit-Reset` / `Retry-After` in the
  error — back off, do not hammer.

## Safety

`prospect create/update`, `account create/update`, `enrollment add`, and the
`task`/`enrollment` actions **change data in the user's live Outreach org and
can send outbound email cadences**. Follow the sensitive-operation rule from
`../SKILL.md`: confirm with the user before first-of-kind writes in a
session, and never enroll prospects the user has not sanctioned.
