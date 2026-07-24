# Pennylane (`heliox tool pennylane -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Pennylane is a
**flat provider** (not grouped like `google`): everything after `--` is the
pennylane tool's own CLI. It wraps the Pennylane external REST API **v2**
(`app.pennylane.com/api/external/v2`) — accounting, invoicing, banking, and
ledger for a single company.

```bash
heliox tool pennylane [--account <company-id>] -- <resource> <verb> [flags...]
```

A connection is bound to **one Pennylane company**. When more than one company
is connected, a `409` lists the candidate company ids; re-run with
`--account <company-id>` before the `--`.

## Command surface

Success prints the provider's JSON response body verbatim; errors render as a
plain message (or, with the global `--json`, a `{"error":{…}}` envelope). Reads
are `list` / `get`; the only mutating verbs are the two `create`s and
`transaction categorize`.

```bash
# Customers — READ covers both company + individual; CREATE is company-only
heliox tool pennylane -- customer list [--cursor <c>] [--filter <expr>] [--limit N] [--sort -id]
heliox tool pennylane -- customer get <id>
heliox tool pennylane -- customer create --body '{"name":"ACME","emails":["ap@acme.example"]}'

# Suppliers (read-only)
heliox tool pennylane -- supplier list
heliox tool pennylane -- supplier get <id>

# Customer invoices (AR) — the highest-value write
heliox tool pennylane -- customer-invoice list [--filter <expr>] [--cursor <c>]
heliox tool pennylane -- customer-invoice get <id>
heliox tool pennylane -- customer-invoice create --body '<invoice-json>'

# Supplier invoices (AP, read-only) — "what is unpaid / unvalidated"
heliox tool pennylane -- supplier-invoice list [--filter <expr>]
heliox tool pennylane -- supplier-invoice get <id>

# Products (invoice line items)
heliox tool pennylane -- product list
heliox tool pennylane -- product get <id>

# Bank transactions — list/get, then categorize
heliox tool pennylane -- transaction list [--cursor <c>] [--filter <expr>]
heliox tool pennylane -- transaction get <id>
heliox tool pennylane -- transaction categorize <id> --body '[{"id":59,"weight":"1"}]'

# Ledger / accounting reports (read-only)
heliox tool pennylane -- ledger trial-balance
heliox tool pennylane -- ledger entries [--cursor <c>]
heliox tool pennylane -- ledger journals
heliox tool pennylane -- ledger accounts
```

Run `-- <resource> --help` (or `-- <resource> <verb> --help`) for exact flags
rather than guessing.

## Footguns (where agents go wrong)

- **Customer read vs create is asymmetric.** `customer list` and `customer get`
  return **both** company and individual customers, but there is **no**
  `POST /customers` — `customer create` posts to `/company_customers` (a B2B
  company customer). To find a customer id for an invoice, `customer list`/`get`;
  to make a new billable company, `customer create`.
- **`categorize` takes a JSON ARRAY, not an object.** The `--body` for
  `transaction categorize` is an array of `{"id":<category-id>,"weight":"<w>"}`
  and **the weights of categories in one group must sum to `1`** (e.g. a 50/50
  split is `[{"id":59,"weight":"0.5"},{"id":33,"weight":"0.5"}]`).
- **Pagination is cursor-based and the tool does NOT auto-loop.** A `list`
  returns one page plus a cursor in its metadata; pass it back via `--cursor`
  to get the next page. Use `--limit` (1–100) to size a page; `--filter` and
  `--sort -id` narrow/order results (the filter grammar is Pennylane's — see
  the field's docs).
- **Request bodies go in `--body` as raw JSON.** The global `--json` is the
  output/error format flag, so create/categorize payloads use `--body '<json>'`
  (object or array). An empty or malformed `--body` is a usage error (exit 2)
  and sends nothing.
- **Scopes are read-biased.** The connection requests read-only ledger scopes,
  so `ledger *` is read-only by design; a `403` on a write means the scope
  wasn't granted, not a transient error.

## Safety

- `customer-invoice create` issues a real accounts-receivable document, and
  `transaction categorize` mutates the books. Treat both as
  finance-mutating: confirm the amounts, customer, and category with the user
  before running, and honor the tool skill's approval gate.
- Reads (`list` / `get` / `ledger *`) are safe and need no confirmation.
