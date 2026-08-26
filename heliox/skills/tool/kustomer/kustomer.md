# Kustomer (`heliox tool kustomer -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Kustomer is a
**flat provider** (not grouped): everything after `--` is the kustomer tool's
own CLI. Kustomer is an omnichannel support CRM: customers, their conversations
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
heliox tool kustomer -- message create <conversation-id> --data '<json>' --json   # replies to the customer, outward-facing
heliox tool kustomer -- note list <conversation-id> --json
heliox tool kustomer -- note create <conversation-id> --data '{"note":"internal only"}' --json
```

### Search

```bash
heliox tool kustomer -- search customers --data '<query-json>' --json    # POST /customers/search
```

## Notes and footguns

- **Filter/query bodies** for `search` and the exact attribute shapes for
  `create`/`update` are Kustomer-specific: consult the customer's Kustomer API
  reference for the body JSON; the tool passes it through unchanged.
- **`message create` is outward-facing**: it posts a reply the customer sees.
  Follow the sensitive-operation rule in `../SKILL.md`: confirm intent
  before sending. Use `note create` for anything that should stay internal.
- **`--query key=value`** (repeatable) adds arbitrary filters to any list/get
  command beyond `--page` / `--page-size`.
- **The connection is a Kustomer API key the user creates**, not an OAuth
  grant, so there is no auth link to relay. A key comes from Settings >
  Security > API Keys > Add API Key inside their own Kustomer org, and the
  admin picks its roles there. Ask for the capability roles the work needs
  (`org.permission.customer.read`, `.conversation.read/.create`,
  `.message.read/.create`, `.note.read/.create`) **plus `org.user`**. That
  last one is not optional and is not obvious: Helio verifies the key against
  `/v1/users/current` before storing it, and a key without `org.user` is
  refused at connect with an error that does not name the missing role.
  `org.admin` is never needed.
- On `401`, the key was deleted or its roles were narrowed. The user replaces
  it in Kustomer and reconnects with the new value.
