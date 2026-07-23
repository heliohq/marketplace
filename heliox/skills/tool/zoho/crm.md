# Zoho CRM (`heliox tool zoho crm -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Zoho CRM is one
app in the **`zoho` group** (`heliox tool zoho books` / `zoho crm`); each app is
its own connection with its own consent. Everything after `--` is the Zoho CRM
tool's own CLI.

```bash
heliox tool zoho crm [--account <key>] -- <resource> <verb> [flags...]
```

The tool wraps the **Zoho CRM REST API v8**. Records live in **modules**
(`Leads`, `Contacts`, `Accounts`, `Deals`, `Tasks`, `Events`, `Calls`, plus any
custom module). `--module` takes the module **API name** and is passed through
verbatim, so custom modules work. On success the provider's JSON is printed
verbatim; an empty search returns nothing (a 204) and still exits 0.

## The mental model (read this first — it prevents the #1 footgun)

Zoho create/update bodies are keyed by **field API names** (`Last_Name`, not
"Last Name"; `Deal_Name`; `Stage`), which differ from the labels you see in the
UI. **Discover them before writing:**

```bash
heliox tool zoho crm -- module list --json                 # available modules
heliox tool zoho crm -- field list --module Leads --json   # a module's field API names
```

Guessing field names is the most common cause of `INVALID_DATA`. Run
`field list` first whenever you are unsure.

## Core commands

### Read / look up

```bash
# search: exactly ONE selector (criteria | email | phone | word)
heliox tool zoho crm -- record search --module Contacts --email jane@acme.com --json
heliox tool zoho crm -- record search --module Leads --criteria '(Last_Name:equals:Doe)' --json
heliox tool zoho crm -- record search --module Deals --word "acme renewal" --json

# list (fields is REQUIRED — run `field list` first)
heliox tool zoho crm -- record list --module Deals --fields Deal_Name,Stage,Amount --per-page 50 --json
heliox tool zoho crm -- record get --module Deals --id 555 --fields Deal_Name,Amount --json

# COQL — precise filtered/aggregated reads (also reads fresh writes that search may 204 on)
heliox tool zoho crm -- query --coql 'select Last_Name, Email from Leads where Email is not null limit 200' --json
```

### Write

```bash
# create: --data is a JSON object (one record) or array (bulk, up to 100)
heliox tool zoho crm -- record create --module Leads --data '{"Last_Name":"Doe","Company":"Acme"}' --json
heliox tool zoho crm -- record update --module Deals --id 999 --data '{"Stage":"Closed Won"}' --json
heliox tool zoho crm -- record delete --module Leads --id 42
heliox tool zoho crm -- record delete --module Leads --ids 1,2,3

# suppress workflows/approvals/blueprints on a write
heliox tool zoho crm -- record create --module Leads --data '{...}' --no-triggers --json
```

### Notes, users, org

```bash
heliox tool zoho crm -- note list --module Deals --id 12 --json
heliox tool zoho crm -- note add --module Leads --id 34 --title "Call summary" --content "Discussed renewal"
heliox tool zoho crm -- user me --json          # the connected user
heliox tool zoho crm -- user list --type ActiveUsers --json
heliox tool zoho crm -- org get --json
```

Run `-- <resource> --help` (or `-- <resource> <verb> --help`) for exact flags
rather than guessing.

## Footguns (the important part — where agents go wrong)

- **Write with field API names, not labels.** `field list --module <M>` first;
  `Last_Name`, not "Last Name". A wrong key returns `INVALID_DATA`.
- **`record list` requires `--fields`** (the v8 API mandates it, max 50). The
  error tells you to run `field list`. `--page` covers the first 2,000 records;
  beyond that use the response's `next_page_token` via `--page-token` (which is
  mutually exclusive with `--page`).
- **`record search` takes exactly one selector.** Passing two is a usage error
  (the API would silently prioritize; the CLI makes it explicit). Search needs
  the `ZohoSearch.securesearch.READ` scope — a `401 OAUTH_SCOPE_MISMATCH` means
  the connection is missing it (reconnect).
- **Freshly written records may 204 on search** (Zoho's search index lags).
  Read them immediately with `query --coql ...` instead.
- **Bulk writes can partially succeed** (HTTP 207): each record in the response
  `data[]` carries its own `code`/`status`. A zero exit does NOT mean every
  record succeeded — inspect the per-record codes.
- **`--no-triggers` suppresses automations** (workflows/approvals/blueprints).
  Omit it to let the org's automations run (the default).
- **US datacenter only (V1).** The connection and all endpoints are pinned to
  Zoho's US DC (`.com`). A Zoho account homed in another DC (`.eu`, `.in`,
  `.com.au`, `.jp`, …) fails at the token layer with an explicit error — it is
  not silently retried. Non-US orgs are not yet supported.
- **`--account` when more than one Zoho account is connected.** A `409` lists
  the candidate account keys; re-run with `--account <key>` (before the `--`).
  The account key is org-scoped, so the same person on two Zoho orgs is two
  connections.

## Safety

- Creating, updating, and deleting records mutates a shared CRM others rely on —
  follow the sensitive-operation rule in [../SKILL.md](../SKILL.md) before
  writing. Prefer `--no-triggers` only when you deliberately want to skip
  automations, and confirm scope before a bulk `record delete`.
