# FreshBooks (`heliox tool freshbooks -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. FreshBooks is a
**flat provider** (not grouped): everything after `--` is the freshbooks tool's
own CLI. It wraps the FreshBooks **Accounting** API for bookkeeper/ops work:
clients, invoices (incl. send), expenses, estimates, payments, and the billable
item catalog.

```bash
heliox tool freshbooks [--account <accountId>] -- <resource> <verb> [flags...]
```

Output is JSON. List results are unwrapped to a provider-neutral envelope
`{"items":[...],"page":..,"pages":..,"per_page":..,"total":..}`; single
get/create/update emit the resource object directly. Errors under `--json`
render `{"error":{"message":..,"status":<http>,"code":<freshbooks code>}}`.
Exit codes: 0 success · 1 runtime/API failure · 2 usage/parse.

## The account_id footgun (read this first)

Every accounting URL is scoped to an `account_id`, which is **not** the login
identity — it lives in `business_memberships[].business.account_id`. The tool
resolves it automatically:

- **One** accounting account → used silently.
- **Multiple** → the command **fails fast (exit 2)** listing the available ids;
  re-run with `--account <accountId>`. It never guesses.
- **Zero** → exit 1 ("no accounting account").

Discover the mapping with `me`, then pass `--account` to skip the lookup:

```bash
heliox tool freshbooks -- me                         # identity + accounts
heliox tool freshbooks --account <accountId> -- invoice list
```

## Core commands

```bash
# clients — resolve or create the bill-to party
heliox tool freshbooks -- client list [--page N] [--per-page N] [--query 'search[email]=a@b.com']
heliox tool freshbooks -- client get <id>
heliox tool freshbooks -- client create --data '{"organization":"Acme","email":"a@b.com"}'
heliox tool freshbooks -- client update <id> --data '{"phone":"555-0100"}'

# invoices — the AR lifecycle
heliox tool freshbooks -- invoice list [--query 'search[customerid]=42']
heliox tool freshbooks -- invoice get <id>
heliox tool freshbooks -- invoice create --data '{"customerid":42,"create_date":"2026-07-01","lines":[{"name":"Consulting","unit_cost":{"amount":"100.00"},"qty":"3"}]}'
heliox tool freshbooks -- invoice update <id> --data '{"notes":"Net 30"}'
heliox tool freshbooks -- invoice send   <id> [--to buyer@x.com]   # emails the invoice (action_email)
heliox tool freshbooks -- invoice delete <id>                      # soft-delete (vis_state=1)

# expenses, estimates, payments, items
heliox tool freshbooks -- expense  list|get|create|update
heliox tool freshbooks -- estimate list|get|create
heliox tool freshbooks -- payment  list|get|create
heliox tool freshbooks -- item     list|get                        # read-only catalog
```

- `create`/`update` take the resource fields as a JSON object via `--data`
  (or `--file <path>`). Pass the **unwrapped** fields — the tool wraps them in
  the FreshBooks `{invoice: {...}}` / `{client: {...}}` envelope for you.
- `list` supports `--page`, `--per-page`, and repeatable `--query key=value`
  for FreshBooks filters (e.g. `search[customerid]=42`, `search[updated_min]=...`).

## Footguns

- Money fields are objects: `{"amount":"100.00","code":"USD"}`, not bare
  numbers.
- `invoice send` requires the invoice to have a client with an email (or pass
  `--to`); it flips the invoice to sent and emails it.
- `delete` is a soft-delete (sets `vis_state`), not a hard removal.
