# Square (`heliox tool square -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Square is a
**flat provider** (not grouped like `google`): everything after `--` is the
square tool's own CLI.

```bash
heliox tool square [--account <key>] -- <resource> <verb> [flags...]
```

The tool wraps the **Square Connect v2 REST API** (a seller's payments,
orders, customers, catalog, inventory and invoices). Every command emits the
provider's JSON on stdout verbatim, so cursors and Square's `errors[]` reach
you intact. Read verbs never mutate; `create` / `update` / `publish` do.

## The mental model (read this first)

Square is **location-scoped**: most reads and writes hang off a `location_id`.
`location list` is the discovery primitive you call first to get the seller's
locations — feed a returned `location_id` into `invoice list`, order search,
inventory reads, etc.

Square's **search endpoints are POST** (`order search`, `customer search`,
`catalog search`, `invoice search`) and `inventory get` is a POST
batch-retrieve, but they are documented **read-only** — they never mutate. You
pass their request body as raw JSON via `--body`.

## Core commands

### Discover

```bash
heliox tool square -- location list                       # GET /v2/locations
heliox tool square -- location get --location-id <id>     # or 'main'
```

### Payments & orders (read)

```bash
heliox tool square -- payment list --location-id <id> --begin-time <rfc3339> --sort-order DESC --limit 50
heliox tool square -- payment get --payment-id <id>
heliox tool square -- order search --body '{"location_ids":["<id>"],"limit":20}'   # POST lookup
heliox tool square -- order get --order-id <id>
```

### Customers (read + write)

```bash
heliox tool square -- customer list --limit 50
heliox tool square -- customer search --body '{"query":{"filter":{"email_address":{"exact":"a@b.com"}}}}'
heliox tool square -- customer get --customer-id <id>
heliox tool square -- customer create --body '{"given_name":"Ada","email_address":"ada@example.com"}'
heliox tool square -- customer update --customer-id <id> --body '{"note":"VIP"}'
```

### Catalog & inventory (read)

```bash
heliox tool square -- catalog list --types ITEM,ITEM_VARIATION
heliox tool square -- catalog search --body '{"object_types":["ITEM"],"query":{"text_query":{"keywords":["latte"]}}}'
heliox tool square -- catalog get --object-id <id> --include-related
heliox tool square -- inventory get --body '{"catalog_object_ids":["<variation-id>"],"location_ids":["<id>"]}'
```

### Invoices (read + write)

```bash
heliox tool square -- invoice list --location-id <id> --limit 50          # location_id is REQUIRED
heliox tool square -- invoice search --body '{"query":{"filter":{"location_ids":["<id>"]}}}'
heliox tool square -- invoice get --invoice-id <id>
heliox tool square -- invoice create --body '{"invoice":{...},"idempotency_key":"<uuid>"}'
heliox tool square -- invoice publish --invoice-id <id> --body '{"version":0,"idempotency_key":"<uuid>"}'
```

### Raw escape hatch

For endpoints not yet wrapped as first-class commands (loyalty,
subscriptions, team, …):

```bash
heliox tool square -- api GET /v2/subscriptions
heliox tool square -- api POST /v2/subscriptions --body '{...}'
```

The path starts at `/v2/…`; `Authorization: Bearer` and the `Square-Version`
header are injected for you.

## Footguns

- **`invoice list` requires `--location-id`.** Square's ListInvoices is
  location-scoped; omit it and the command fails as a usage error before any
  request goes out. Run `location list` first.
- **Writes are side-effecting and need an idempotency key.** `customer create`,
  `invoice create`, and `invoice publish` mutate the seller's account. Square's
  create/publish bodies expect an `idempotency_key` (a UUID you generate) so a
  retry doesn't double-create.
- **Search is POST but read-only.** `order/customer/catalog/invoice search` and
  `inventory get` take `--body '<json>'`; they are lookups, not mutations.
- **Amounts are integer minor units.** Square money fields are `{amount, currency}`
  where `amount` is the smallest currency unit (cents), not a decimal.
