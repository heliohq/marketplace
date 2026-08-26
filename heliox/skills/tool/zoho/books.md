# Zoho Books (`heliox tool zoho books -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Zoho Books is
one app in the **`zoho` group** (`heliox tool zoho books` / `zoho crm`); each
app is its own connection with its own consent. Everything after `--` is the
Zoho Books tool's own CLI.

```bash
heliox tool zoho books [--account <key>] -- <resource> <verb> [flags...]
```

The tool wraps the **Zoho Books REST API v3**. On success the provider's JSON
is printed verbatim (including the `page_context` object on lists, so you can
page); a failure exits non-zero with Zoho's `code`/`message`.

## The mental model (read this first: it prevents the #1 footgun)

**Every command except `org list` requires `--organization-id`.** A Zoho login
can own several Books organizations, and the org id is a per-call selector that
is neither in the token nor guessable. Discover it first:

```bash
heliox tool zoho books -- org list --json          # NO --organization-id; yields the ids
```

Then pass `--organization-id <id>` on every other command. Omitting it is a
usage error that tells you to run `org list`; there is no "default org"
fallback.

## Core commands

### Receivables: "did customer X pay? what's outstanding?"

```bash
# invoices, filtered by customer and/or status view
heliox tool zoho books -- invoice list --organization-id O --customer-id C --filter-by Status.Overdue --json
heliox tool zoho books -- invoice get  --organization-id O --id 460000000012345 --json

# customer payments (GET /customerpayments)
heliox tool zoho books -- payment list --organization-id O --customer-id C --json
```

### Look up a customer or vendor

```bash
# contacts are customers AND vendors, split by contact_type
heliox tool zoho books -- contact list --organization-id O --contact-type customer --search-text acme --json
heliox tool zoho books -- contact list --organization-id O --contact-type vendor --json
heliox tool zoho books -- contact get  --organization-id O --id 460000000067890 --json
```

### Items, bills, expenses

```bash
heliox tool zoho books -- item    list --organization-id O --search-text hosting --json  # rates for line items
heliox tool zoho books -- item    get  --organization-id O --id I1 --json
heliox tool zoho books -- bill    list --organization-id O --vendor-id V --filter-by Status.Overdue --json
heliox tool zoho books -- expense list --organization-id O --filter-by Status.Unbilled --json
```

### Create (from a conversation)

`--data` is a **flat JSON object** sent verbatim as the request body (Books does
NOT use a `{"data":[…]}` wrapper). Compose line items after an `item list` /
`contact list` lookup.

```bash
heliox tool zoho books -- contact  create --organization-id O --data '{"contact_name":"Acme Inc","contact_type":"customer"}' --json
heliox tool zoho books -- invoice  create --organization-id O --data '{"customer_id":"C1","line_items":[{"item_id":"I1","rate":100,"quantity":2}]}' --json
heliox tool zoho books -- estimate create --organization-id O --data '{"customer_id":"C1","line_items":[{"name":"Consulting","rate":150,"quantity":4}]}' --json
heliox tool zoho books -- expense  create --organization-id O --data '{"account_id":"A1","paid_through_account_id":"P1","amount":42.5}' --json
```

Run `-- <resource> --help` (or `-- <resource> <verb> --help`) for exact flags
rather than guessing.

## Footguns (the important part: where agents go wrong)

- **`--organization-id` is required everywhere except `org list`.** Run
  `org list` first and reuse the id. A missing id is a usage error, never a
  silent default.
- **Filters are pass-through.** `--filter-by` takes Books status views verbatim
  (`Status.Overdue`, `Status.Sent`, `Status.Paid`, `Status.Unbilled`, …);
  `--status`, `--customer-id`, `--vendor-id`, `--contact-type`, `--search-text`,
  `--page`, `--per-page` map straight to Books query params. `per_page` defaults
  to 200; page with `--page` while `page_context.has_more_page` is true.
- **Create bodies are flat.** Put `line_items` and every field directly inside
  `--data`; there is no `{"data":[…]}` envelope (this differs from Zoho CRM).
- **Errors carry an integer `code`.** Books returns `{"code":<int>,"message":…}`
  where `code` 0 means success. A wrong value returns a non-zero code (e.g.
  `code 15` for a bad filter). A `401` means the token is invalid; reconnect.
- **US datacenter only (V1).** The connection and all endpoints are pinned to
  Zoho's US DC (`.com`). A Zoho account homed in another DC (`.eu`, `.in`,
  `.com.au`, `.jp`, …) fails at the token layer with an explicit error; it is
  not silently retried. Non-US orgs are not yet supported.
- **`--account` when more than one Zoho account is connected.** A `409` lists
  the candidate account keys; re-run with `--account <key>` (before the `--`).
  The account key is account-level (one Zoho user), so one connection still
  addresses every organization that user can see via `--organization-id`.

## Safety

- Creating invoices, estimates, contacts, and expenses mutates shared
  accounting records others rely on. Follow the sensitive-operation rule in
  [../SKILL.md](../SKILL.md) before writing, and confirm the target
  organization id first.
