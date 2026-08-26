# Gorgias (`heliox tool gorgias -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Gorgias is a
**flat provider** (not grouped like `google`): everything after `--` is the
gorgias tool's own CLI.

```bash
heliox tool gorgias [--account <key>] -- <resource> <verb> [flags...]
```

Gorgias is a helpdesk / customer-support platform. This tool wraps the
read/reply/triage slice of the REST API a support agent works from: tickets and
their messages, customer lookup, agents, tags, saved views, satisfaction
surveys, and the account identity anchor.

## The mental model (read this first)

- Every Gorgias helpdesk is a **per-subdomain instance** (`acme.gorgias.com`).
  You never pass the subdomain: it is captured at connect time and injected
  for you, so the tool always talks to the right account.
- A **ticket** is one customer conversation. Its reply thread lives in its
  **messages** (`message list <ticket-id>` / `message create <ticket-id>`),
  not in the ticket object itself.
- **Views** are the saved queues agents work from (e.g. "Open", "Unassigned").
  `view list` shows them; `view items <view-id>` returns the tickets in one.
- List commands are **cursor-paginated**: the response is
  `{"data":[...],"meta":{"next_cursor":"...","prev_cursor":null}}`. Pass
  `meta.next_cursor` back as `--cursor` to page forward; a `null` cursor means
  no further page.

## Core commands

### Read / triage

```bash
# The saved queues, then the tickets in one
heliox tool gorgias -- view list --json
heliox tool gorgias -- view items 42 --json

# List tickets (filters: --view, --customer, --external-id, --trashed)
heliox tool gorgias -- ticket list --view 42 --limit 30 --json
heliox tool gorgias -- ticket list --cursor "<next_cursor>" --json

# One ticket and its whole conversation
heliox tool gorgias -- ticket get 12345 --json
heliox tool gorgias -- message list 12345 --json
```

### Look up a customer

```bash
# Find by email or name (this IS the lookup: there is no separate search verb)
heliox tool gorgias -- customer list --email jane@acme.com --json
heliox tool gorgias -- customer get 987 --json
```

### Reply / update

```bash
# Post a reply on a ticket (from an agent). The default --channel api needs no
# routing addresses: use it unless the reply must go out over a real channel.
heliox tool gorgias -- message create 12345 --body "Thanks, shipping today!" \
  --from-agent --sender-email support@acme.com --json

# Reply over the email channel: it also needs a source (routing) object. The
# --source-from address MUST be an email integration already connected to
# Gorgias, or the API rejects the send.
heliox tool gorgias -- message create 12345 --body "Thanks, shipping today!" \
  --channel email --from-agent --sender-email support@acme.com \
  --source-from support@acme.com --source-to jane@acme.com --json

# Change status / assignee / priority / tags (PUT replaces the tag set)
heliox tool gorgias -- ticket update 12345 --status closed --assignee 55 --json
heliox tool gorgias -- ticket update 12345 --tag vip --tag refund --json

# Open a new ticket with an initial customer message (default --channel api)
heliox tool gorgias -- ticket create --customer-email jane@acme.com \
  --subject "Order help" --body "Where is my order?" --json
```

### Reference / reporting

```bash
heliox tool gorgias -- user list --json          # agents (resolve assignees)
heliox tool gorgias -- tag list --json           # tags for triage
heliox tool gorgias -- satisfaction list --json  # CSAT survey results
heliox tool gorgias -- account get --json        # identity / health-check
```

## Conventions

- `--json` on any subcommand emits the raw Gorgias JSON (the paginated
  envelope for lists, the resource object otherwise). Without it you still get
  JSON: the tool is machine-first.
- **Exit codes:** `0` success, `1` API/runtime failure (a typed error carrying
  the Gorgias message + HTTP status; a `401` also signals the connection needs
  reconnecting), `2` usage/parse error.
- IDs are integers. `ticket get`, `message list/create`, `customer get`,
  `user get`, `view items` take the id as a positional argument.

## Footguns

- **`ticket update` replaces the tag set.** `--tag` (repeatable) sets the
  ticket's complete tags, it does not append to existing tags: read the
  ticket first if you need to preserve current tags.
- **A message's `from_agent` decides the voice.** Omit `--from-agent` and the
  message is attributed to the customer; pass it for an agent reply. Set
  `--sender-email` to the right party.
- **Channel picks the required fields.** `message create` / `ticket create`
  default to `--channel api` (valid: `api|email|phone|sms|internal-note`), and
  the tool always sends the `via` Gorgias requires (derived from the channel,
  or set it explicitly with `--via api|email|internal-note`). The `email`,
  `phone`, and `sms` channels additionally need a source (routing) object:
  supply `--source-from` and one or more `--source-to`; for email the
  `--source-from` address must be an email integration connected to Gorgias.
  When in doubt, stay on `api`: it delivers the message into the ticket without
  any routing setup.
- **Filter tickets with views, not ad-hoc status flags.** Gorgias' ticket list
  has no `status`/`assignee` query filter: those live in views. Use
  `--view <id>` (or `--customer <id>`) to scope the queue.
