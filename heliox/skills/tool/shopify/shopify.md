# Shopify (`heliox tool shopify -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Shopify is a
**flat provider** (not grouped like `google`): everything after `--` is the
shopify tool's own CLI.

```bash
heliox tool shopify [--account <shop>] -- <resource> <verb> [flags...]
```

Every subcommand runs against the **GraphQL Admin API** under the hood (a
single `POST /admin/api/<version>/graphql.json`), so you never hand-write
GraphQL for the common cases — but a raw `graphql` passthrough is there when you
need it. The REST Admin API is legacy and unavailable to this app.

## Connect (instance-scoped)

Shopify is **per-store**: the connection is tied to one `{shop}.myshopify.com`.
When you run `heliox tool shopify auth`, you must supply the shop domain (the
`myshopify.com` host, e.g. `acme.myshopify.com` — or just `acme`). The stored
account key IS that shop host, so `--account <shop>` selects it on later calls.

## Core commands

### Read (side-effect free)

```bash
heliox tool shopify -- shop info                                  # store identity, currency, plan
heliox tool shopify -- product list --limit 20 --query "status:active"
heliox tool shopify -- product get <id>                          # numeric id or gid://shopify/Product/<id>
heliox tool shopify -- order list --limit 20                     # newest first
heliox tool shopify -- order get <id>
heliox tool shopify -- customer list --query "email:jane@acme.com"
heliox tool shopify -- customer get <id>
heliox tool shopify -- inventory levels <inventory-item-id>      # stock by location
```

Cursor pagination: `--limit` maps to GraphQL `first`; `--after <end_cursor>`
resumes from a prior response's `page_info.end_cursor`. Lists return
`{"<resource>":[...], "page_info":{"has_next_page":..,"end_cursor":..}}`. The
tool never auto-follows pages.

### Write (side-effecting)

```bash
heliox tool shopify -- product update <id> --status ACTIVE       # ACTIVE|DRAFT|ARCHIVED
heliox tool shopify -- product create --title "Tee" --status DRAFT
heliox tool shopify -- customer create --email jane@acme.com --first-name Jane
heliox tool shopify -- customer update <id> --note "VIP"
heliox tool shopify -- order update <id> --note "..." --tag priority --tag reviewed
heliox tool shopify -- inventory adjust --item <id> --location <id> --delta 5
```

### Escape hatch — raw GraphQL

```bash
heliox tool shopify -- graphql --query 'query{ shop { name } }'
heliox tool shopify -- graphql --query 'mutation(...){ ... }' --variables '{"k":"v"}'
```

Use this for anything the modeled verbs do not cover (fulfillments, price rules,
metafields, draft-order completion, …). Ids are Shopify GIDs
(`gid://shopify/<Type>/<n>`); the modeled `get`/`update` verbs also accept a
bare numeric id and normalize it.

## Footguns

- **Mutation `userErrors` are failures, not warnings.** Shopify returns HTTP 200
  even when a write is rejected, carrying a `userErrors` array. This tool treats
  a non-empty `userErrors` as a **non-zero exit with the messages** — it never
  reports a no-op write as success. Read the error, fix the input, retry.
- **Protected customer data may be redacted.** Order/customer PII (name, email,
  address) requires Shopify's Protected Customer Data approval on production
  stores; on an unapproved app those fields come back null/redacted even though
  the call succeeds.
- **Pin the API version if you depend on a field.** The tool pins a stable
  quarterly version by default; pass `--api-version YYYY-MM` only when you need a
  specific one.
