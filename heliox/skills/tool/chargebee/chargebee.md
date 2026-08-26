# Chargebee (`heliox tool chargebee -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Chargebee is a
**flat provider** (not grouped like `google`): everything after `--` is the
chargebee tool's own CLI over the Chargebee Billing **v2 REST API**.

```bash
heliox tool chargebee [--account <site>] -- <resource> <verb> [flags...]
```

One connected account is one Chargebee **site** (e.g. `acme-test`). The account
key shown in `heliox tool list` is the site subdomain. Credentials (the site
API key) are injected automatically: you never see or pass them.

## The mental model

- **Reads return Chargebee's native JSON** on stdout. List responses are
  `{ "list": [ { "<resource>": {…} }, … ], "next_offset": "<cursor>" }`;
  single-object reads are `{ "<resource>": {…} }`. Page with `--limit` (≤100)
  and feed the returned `next_offset` back as `--offset`.
- **Filters use Chargebee's bracket-operator syntax**, passed verbatim:
  `--filter "status[is]=active"`, `--filter "id[in]=[\"cust_1\",\"cust_2\"]"`
  (repeatable).
- **Writes are typed flags**, serialized as form-encoded requests (the tool
  handles Chargebee's bracketed encoding for you). Flat fields go through
  repeatable `--param key=value`; subscription line items go through
  `--item-price id[:quantity]`.

## Core commands

### Read (each resource: `list` + `get <id>`)

```bash
heliox tool chargebee -- customer list --limit 20 --filter "auto_collection[is]=on" --json
heliox tool chargebee -- customer get <customer-id> --json
heliox tool chargebee -- subscription list --filter "status[is]=active" --json
heliox tool chargebee -- subscription get <subscription-id> --json
heliox tool chargebee -- invoice list --filter "status[is]=payment_due" --json
heliox tool chargebee -- invoice get <invoice-id> --json
heliox tool chargebee -- credit-note list --json
heliox tool chargebee -- item list --json          # Product Catalog 2.0 items
heliox tool chargebee -- item-price list --json     # PC 2.0 prices
heliox tool chargebee -- plan list --json           # PC 1.0 plans
heliox tool chargebee -- payment-source list --json
heliox tool chargebee -- transaction list --json
heliox tool chargebee -- event list --json          # billing activity stream
heliox tool chargebee -- usage list --json          # metered usage (top-level)
```

### Invoice PDF

`invoice pdf` is a **POST** that returns a JSON `download` object: a transient
`download_url` plus `valid_till`, not raw PDF bytes. Fetch the URL before it
expires.

```bash
heliox tool chargebee -- invoice pdf <invoice-id> --json
```

### Write

```bash
# customers
heliox tool chargebee -- customer create --param first_name=Ada --param email=ada@example.com --json
heliox tool chargebee -- customer update <customer-id> --param company="Acme Inc" --json

# subscriptions: --item-price is repeatable; append :qty for a quantity
heliox tool chargebee -- subscription create --customer-id <id> \
  --item-price basic-USD:1 --item-price addon-USD --param auto_collection=on --json
heliox tool chargebee -- subscription change <subscription-id> --item-price pro-USD --json
heliox tool chargebee -- subscription cancel <subscription-id> --param end_of_term=true --json
heliox tool chargebee -- subscription reactivate <subscription-id> --json

# metered usage: creation is ALWAYS subscription-scoped (no flat POST /usages)
heliox tool chargebee -- usage create --subscription-id <id> \
  --param item_price_id=metered-USD --param quantity=5 --json
```

### Escape hatch (read-only)

For the long tail (quotes, estimates, orders, exports) not wrapped as a verb,
GET any v2 path:

```bash
heliox tool chargebee -- get --path /quotes --query limit=5 --json
```

## Footguns

- **`usage create` needs `--subscription-id`.** There is no flat
  `POST /usages`; usage is always recorded against a subscription.
- **`invoice pdf` returns a link, not bytes.** Use the `download_url` from the
  response, and note `valid_till`: it expires.
- **Item prices, not plans, for PC 2.0.** New subscriptions use
  `--item-price` (`item_prices`); `plan list` is the legacy PC 1.0 surface.
- **Paging is opaque cursors.** Pass the response's `next_offset` back as
  `--offset`; don't compute offsets yourself.
