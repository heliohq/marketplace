# Kit / ConvertKit (`heliox tool kit -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Kit is a
**flat provider** (not grouped like `google`): everything after `--` is the
kit tool's own CLI. Kit is creator email marketing (formerly ConvertKit); this
tool wraps the **V4 API** at `api.kit.com/v4` over your OAuth connection.

```bash
heliox tool kit [--account <key>] -- <resource> <verb> [flags...]
```

Connect once with `heliox tool kit auth`; then every command runs against the
connected Kit account. Commands are grouped by resource: `account`,
`subscriber`, `tag`, `broadcast`, `sequence`, `custom-field`, `form`,
`segment`.

## Output & errors (read once)

- Every command prints one JSON envelope: `{ "data": ... }`, plus
  `{ "pagination": {...} }` on list commands. The resource is lifted out of
  Kit's per-endpoint wrapper into a stable `data` key, so keys are consistent
  regardless of endpoint.
- Add `--json` to also get errors as a structured envelope
  `{ "error": { "message", "kind", "status" } }` (`kind` is `usage` or `api`;
  `status` is the HTTP status on API errors). Exit code: `0` success,
  `1` runtime/API failure, `2` usage/parse error.

## Pagination (cursor-based, one page per call)

List commands accept `--limit` (Kit `per_page`), `--after`, and `--before`.
They return **one page** and never auto-follow cursors. To page forward, read
`pagination.end_cursor` from the envelope and pass it as `--after` on the next
call (use `pagination.start_cursor` with `--before` to page back).

```bash
heliox tool kit -- subscriber list --limit 100 --json
# → { "data": [...], "pagination": { "has_next_page": true, "end_cursor": "X" } }
heliox tool kit -- subscriber list --limit 100 --after X --json
```

## Account (identity + stats)

```bash
heliox tool kit -- account get --json              # whoami + plan
heliox tool kit -- account stats --growth --json   # list growth stats
heliox tool kit -- account stats --email --json    # email send/open/click stats
```

`account stats` requires exactly one of `--growth` / `--email`.

## Subscribers (the contact list)

```bash
# filter by status / email / created window; paginate as above
heliox tool kit -- subscriber list --status active --created-after 2026-01-01T00:00:00Z --json
heliox tool kit -- subscriber get <id> --json
# create/upsert; --fields sets custom field values as key=value pairs
heliox tool kit -- subscriber create --email a@example.com --first-name Ada --fields plan=pro --json
heliox tool kit -- subscriber update <id> --first-name Grace --json
heliox tool kit -- subscriber unsubscribe <id> --json
```

`--status` is one of `active|inactive|bounced|complained|cancelled|all`.

## Tags (audience segmentation — Kit's automation trigger primitive)

```bash
heliox tool kit -- tag list --json
heliox tool kit -- tag create --name "VIP" --json
# add/remove a tag; target the subscriber by id XOR email (not both)
heliox tool kit -- tag add    --tag-id 5 --email a@example.com --json
heliox tool kit -- tag remove --tag-id 5 --subscriber-id 123 --json
```

## Broadcasts (newsletters — the highest-value action)

```bash
heliox tool kit -- broadcast list --json
heliox tool kit -- broadcast get <id> --json
# create a DRAFT (omit --send-at); add --send-at to schedule
heliox tool kit -- broadcast create --subject "Hello" --content "<p>Hi</p>" --json
heliox tool kit -- broadcast create --subject "Launch" --content "<p>...</p>" \
  --send-at 2026-08-01T15:00:00Z --public --tag-id 5 --json
heliox tool kit -- broadcast update <id> --subject "New subject" --json
heliox tool kit -- broadcast stats <id> --json     # open/click stats
```

`--content` is HTML. `--tag-id` / `--segment-id` restrict recipients (Kit
`subscriber_filter`). `--public` publishes to the web newsletter feed.

## Sequences, forms, custom fields, segments

```bash
# sequences (automations): list + enroll a subscriber (id XOR email)
heliox tool kit -- sequence list --json
heliox tool kit -- sequence add --sequence-id 9 --email a@example.com --json

# forms: list + subscribe a contact via a form (id XOR email)
heliox tool kit -- form list --json
heliox tool kit -- form add --form-id 12 --email a@example.com --json

# custom fields: read/create the per-subscriber data model
heliox tool kit -- custom-field list --json
heliox tool kit -- custom-field create --label "Company" --json

# segments: enumerate saved segments for broadcast targeting
heliox tool kit -- segment list --json
```

## Footguns

- **Subscriber id XOR email.** `tag add/remove`, `sequence add`, and `form add`
  need exactly one of `--subscriber-id` or `--email`. Passing both (or neither)
  is a usage error (exit 2).
- **A broadcast without `--send-at` is a draft.** It is not sent until you set a
  future `--send-at` (or send it from the Kit UI). `--public` only controls the
  web feed, not delivery.
- **Lists are one page.** Nothing auto-paginates; walk `pagination.end_cursor`
  yourself with `--after` when you need more than one page.
