# Lemon Squeezy (`heliox tool lemon-squeezy -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Lemon Squeezy
is a **flat provider** (not grouped like `google`): everything after `--` is
the lemon-squeezy tool's own CLI.

```bash
heliox tool lemon-squeezy [--account <key>] -- <resource> <verb> [flags...]
```

Connect is an **API key**, not OAuth: the user mints a key in the Lemon Squeezy
dashboard (Settings → API) and pastes it into the connect drawer. There are no
scopes — a key grants full account access.

## Output and error shape

Every command prints the provider's **JSON:API document verbatim** on stdout —
the `{data, meta, links, included}` envelope. You never hand-build the
bracketed JSON:API query syntax; the flags below map to it. Errors surface
Lemon Squeezy's `{"errors":[{status,title,detail}]}` body. Exit codes: `0`
success, `1` API/runtime failure (e.g. a 429 rate limit — 300 req/min — or a
401), `2` usage/parse error. Add `--json` for the structured error envelope.

## List / read flags (every `list` and `get`)

- `--page <n>` / `--page-size <n>` — JSON:API paging (`page[number]` /
  `page[size]`).
- `--filter <key>=<value>` — repeatable; each becomes `filter[key]=value`.
- `--include <a,b>` — comma-separated related resources to embed.

```bash
heliox tool lemon-squeezy -- whoami                       # GET /users/me (identity)
heliox tool lemon-squeezy -- store list --page 1 --page-size 50
heliox tool lemon-squeezy -- order list --filter store_id=123 --include customer
heliox tool lemon-squeezy -- subscription get 456 --include order
```

## Resource groups

Each group has `list` and `get <id>`; some add write/action verbs:

- **store** · **product** · **variant** · **price** · **file** · **order-item**
  · **license-key-instance** — read-only (`list`, `get`).
- **order** — `list`, `get`, `refund <id>`, `invoice <id>`.
- **customer** — `list`, `get`, `create`, `update <id>`.
- **subscription** — `list`, `get`, `update <id>`, `cancel <id>` (cancel keeps
  the subscription valid through its grace period).
- **subscription-invoice** — `list`, `get`, `refund <id>`, `invoice <id>`.
- **subscription-item** — `list`, `get`, `update <id>`, `current-usage <id>`.
- **usage-record** — `list`, `get`, `create`.
- **discount** — `list`, `get`, `create`, `delete <id>`.
- **license-key** — `list`, `get`, `update <id>`.
- **checkout** — `list`, `get`, `create` (returns a `url` to send a buyer).
- **webhook** — `list`, `get`, `create`, `update <id>`, `delete <id>`.
- top-level **whoami** — the authenticated user.

## Writes: `--data` is a full JSON:API document

`create` and `update` take `--data` with the provider's JSON:API request body
(a `{"data":{"type":...,"attributes":{...},"relationships":{...}}}` object):

```bash
# Generate a checkout link for a deal
heliox tool lemon-squeezy -- checkout create --data '{
  "data":{"type":"checkouts",
    "relationships":{
      "store":{"data":{"type":"stores","id":"1"}},
      "variant":{"data":{"type":"variants","id":"2"}}}}}'

# Cancel a subscription (grace period, not immediate)
heliox tool lemon-squeezy -- subscription cancel 456
```

## Actions

- `order refund <id>` / `subscription-invoice refund <id>` — omit `--data` for
  a full refund; pass `--data '{"data":{"type":"...","id":"<id>","attributes":{"amount":<cents>}}}'`
  for a partial one.
- `order invoice <id>` / `subscription-invoice invoice <id>` — generate a
  downloadable invoice; invoice fields are query params via repeatable
  `--param key=value` (`name`, `address`, `city`, `state`, `zip_code`,
  `country`, `notes`). The response carries a signed `download_invoice` URL
  under `meta.urls`.
- `subscription-item current-usage <id>` — usage-based billing state.

## Footguns

- **Refunds live on orders and subscription-invoices**, not on a generic
  endpoint — refund a one-off order via `order refund`, a subscription charge
  via `subscription-invoice refund`.
- **`subscription cancel` is a grace-period cancel**, not a hard stop: the row
  goes `cancelled` but stays valid until `ends_at`. To end immediately or
  resume, use `subscription update` with the appropriate attributes.
- **The License API (`/v1/licenses/*`) is out of scope** — it is customer-facing
  and keyed by a license key, not this account API key. Use `license-key` /
  `license-key-instance` for account-side license management.
