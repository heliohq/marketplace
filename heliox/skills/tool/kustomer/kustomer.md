# Kustomer (`heliox tool kustomer -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Kustomer is a
**flat provider** (not grouped): everything after `--` is the kustomer tool's
own CLI. Kustomer is an omnichannel support CRM — customers, their conversations
(tickets), the messages inside them, and internal agent notes.

```bash
heliox tool kustomer [--account <key>] -- <resource> <verb> [flags...]
```

Responses are the provider's JSON:API envelope (`{"data":…,"meta":…,"links":…}`)
passed through **verbatim** on stdout. Page with `--page` / `--page-size`, or
follow `links.next` from a response. Writes take a raw JSON body via `--data`
(or `--file`); the tool does not reshape it, so send Kustomer's documented
attribute shape.

## Command surface

### Customers

```bash
heliox tool kustomer -- customer get <id> --json
heliox tool kustomer -- customer get-by-email bob@acme.com --json     # value is URL-encoded into the path
heliox tool kustomer -- customer conversations <id> --page 1 --page-size 20 --json
heliox tool kustomer -- customer create --data '{"name":"Acme Inc","emails":[{"email":"ops@acme.com"}]}' --json
```

### Conversations (tickets)

```bash
heliox tool kustomer -- conversation get <id> --json
heliox tool kustomer -- conversation list --page 1 --json
heliox tool kustomer -- conversation create --data '<json>' --json
heliox tool kustomer -- conversation update <id> --data '{"status":"done","priority":2}' --json
```

### Messages (the customer-facing thread) and notes (internal)

```bash
heliox tool kustomer -- message list <conversation-id> --json
heliox tool kustomer -- message create <conversation-id> --data '<json>' --json   # replies to the customer — outward-facing
heliox tool kustomer -- note list <conversation-id> --json
heliox tool kustomer -- note create <conversation-id> --data '{"note":"internal only"}' --json
```

### Search

```bash
heliox tool kustomer -- search customers --data '<query-json>' --json    # POST /customers/search
```

## Notes and footguns

- **Filter/query bodies** for `search` and the exact attribute shapes for
  `create`/`update` are Kustomer-specific — consult the customer's Kustomer API
  reference for the body JSON; the tool passes it through unchanged.
- **`message create` is outward-facing**: it posts a reply the customer sees.
  Follow the sensitive-operation rule in `../SKILL.md` — confirm intent
  before sending. Use `note create` for anything that should stay internal.
- **`--query key=value`** (repeatable) adds arbitrary filters to any list/get
  command beyond `--page` / `--page-size`.
- On `401 reconnect required`, the token expired for good (Kustomer refresh
  tokens die after ~2 weeks unused) — relay a fresh `auth` link.
