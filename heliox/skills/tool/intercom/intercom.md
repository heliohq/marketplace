# Intercom (`heliox tool intercom -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Intercom is a
**flat provider** (not grouped like `google`): everything after `--` is the
intercom tool's own CLI.

```bash
heliox tool intercom [--account <key>] -- <resource> <verb> [flags...]
```

Intercom is a customer-support workspace: a shared inbox of **conversations**, a
**contacts/companies** CRM, **tickets**, and a **Help Center** of articles.
Every command hangs under a resource group; output is the provider's JSON
verbatim. Run `-- <resource> --help` (or `-- <resource> <verb> --help`) for the
exact flags rather than guessing.

## Resources

- `conversation` (the inbox): `list`, `search`, `get`, `reply`, `note`,
  `close`, `open`, `snooze`, `assign`, `tag`, `untag`
- `contact` (people): `list`, `search`, `get`, `create`, `update`, `note`, `tag`
- `company` (accounts): `list`, `get`, `upsert`
- `ticket`: `create`, `search`, `get`, `update`, `reply`, `type-list`
- `article` (Help Center): `list`, `get`, `search`, `create`, `update`,
  `collection-list`
- `message` (proactive outreach): `send`
- `admin` (teammates): `me`, `list`, `get`
- `team`: `list`, `get`
- `tag`: `list`, `create`

## Core commands

### Read the inbox

```bash
heliox tool intercom -- conversation list --per-page 30 --json
heliox tool intercom -- conversation get --id 42 --json
# search: raw --query object OR convenience filters (never both)
heliox tool intercom -- conversation search --state open --updated-since 1693782000 --json
heliox tool intercom -- conversation search --query '{"field":"open","operator":"=","value":true}' --json
```

### Act on a conversation

```bash
# reply = customer-visible; note = internal (admins only). Separate verbs on purpose.
heliox tool intercom -- conversation reply --id 42 --body "Let me check on that."
heliox tool intercom -- conversation note  --id 42 --body "customer is on the Pro plan"
heliox tool intercom -- conversation close  --id 42
heliox tool intercom -- conversation snooze --id 42 --snoozed-until 1735689600
heliox tool intercom -- conversation open   --id 42
heliox tool intercom -- conversation assign --id 42 --assignee-id 530165   # admin OR team id
heliox tool intercom -- conversation tag    --id 42 --tag-id 88
heliox tool intercom -- conversation untag  --id 42 --tag-id 88
```

The acting admin is resolved automatically from `/me` when you omit
`--admin-id`; pass `--admin-id` to act as a specific teammate.

### Contacts, companies

```bash
heliox tool intercom -- contact search --email jane@acme.com --json
heliox tool intercom -- contact create --email jane@acme.com --name "Jane" --role user --json
heliox tool intercom -- contact update --id <id> --name "Jane Doe" --json
heliox tool intercom -- contact note   --id <id> --body "VIP; escalate fast"
heliox tool intercom -- company upsert --company-id acme-1 --name "Acme Inc" --json
```

`--body-json '{...}'` on create/update/upsert merges a raw JSON object over the
scalar flags (for custom attributes and fields the flags don't cover).

### Tickets

```bash
heliox tool intercom -- ticket type-list --json                       # get a ticket_type_id first
heliox tool intercom -- ticket create --ticket-type-id 18 --contact-id <cid> \
  --attributes-json '{"_default_title_":"Refund request","priority":"high"}' --json
heliox tool intercom -- ticket update --id <tid> --state in_progress --assignee-id 530165 --json
heliox tool intercom -- ticket reply  --id <tid> --body "Working on it." --message-type comment
```

### Help Center articles

```bash
# article search is a phrase GET (not the POST query model the inbox uses)
heliox tool intercom -- article search --phrase "refund policy" --state published --json
heliox tool intercom -- article create --title "How to request a refund" --author-id <admin-id> \
  --body "<p>Steps…</p>" --state draft --json
```

### Proactive outreach, orientation

```bash
heliox tool intercom -- message send --message-type email --subject "Welcome" \
  --body "Thanks for signing up!" --to-email jane@acme.com
heliox tool intercom -- admin me --json      # who am I + which workspace
heliox tool intercom -- admin list --json
heliox tool intercom -- team list --json
heliox tool intercom -- tag list --json
```

## Footguns (where agents go wrong)

- **`reply` is public; `note` is internal.** `conversation reply` (and
  `ticket reply --message-type comment`) is visible to the customer.
  `conversation note` (and `--message-type note`) is admins-only. Never use
  `reply` for a private aside.
- **Search: `--query` and convenience flags are mutually exclusive.** Give
  *either* a raw Intercom query object via `--query`, *or* the convenience
  filters (`--state`, `--email`, `--updated-since`). Supplying both is a usage
  error. Convenience filters compile into an `AND` group.
- **Pagination is cursor-based.** Responses carry a `pages.next.starting_after`
  cursor; feed it back with `--starting-after` to get the next page
  (`--per-page` up to 150). Search pagination lives in the request body, handled
  for you.
- **Assignment `--assignee-id` takes an admin OR a team id.** `admin list` and
  `team list` give you the ids; `0` unassigns.
- **Companies upsert by `company-id`, not Intercom id.** `company upsert` keys on
  your own `company_id`; `company get --id` takes the Intercom-internal id.
- **`--account` when more than one Intercom workspace is connected.** A `409`
  lists the candidate account keys; re-run with `--account <key>` (before the
  `--`).

## Safety

- Replies and outbound messages reach real customers. Follow the
  sensitive-operation rule in [../SKILL.md](../SKILL.md) before sending a public
  reply, an admin-initiated message, or publishing an article.
- There is no delete command for conversations or contacts by design; clean up
  test artifacts (tags, draft articles) in the Intercom UI.
