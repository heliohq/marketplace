# Xero (`heliox tool xero -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Xero is a
**flat provider** (not grouped like `google`): everything after `--` is the
xero tool's own CLI.

```bash
heliox tool xero [--account <key>] -- <resource> <verb> [flags...]
```

The tool wraps the Xero **Accounting API** (`api.xro/2.0`). It emits Xero's
JSON responses **verbatim**: Xero wraps collections in a PascalCase envelope
(`{"Invoices":[...]}`, `{"Contacts":[...]}`), and that is exactly what you get
on stdout.

## The mental model (read this first: it prevents the #1 footgun)

One Xero login can act on **many organisations** (Xero calls them *tenants*).
A single access token is scoped to the **user**, not one org, and which org a
call hits is chosen per request. So every accounting command needs a target
organisation:

- **One org connected** → it is auto-selected. You do nothing. This is the
  common case and is invisible.
- **More than one org connected** → the command **exits 2** and tells you to
  pass `--tenant`, listing every organisation's name and id. Retry with one.
- **`--tenant <id|name>`** → pick an org explicitly. Accepts the tenant GUID
  directly, or matches an organisation **name** case-insensitively.

List the connected organisations any time:

```bash
heliox tool xero -- connections            # → [{id, tenantId, tenantName, tenantType}, ...]
```

## Core commands

### Read

```bash
heliox tool xero -- organisation get
heliox tool xero -- contact list --query where='Name.Contains("Acme")'
heliox tool xero -- contact get <ContactID>
heliox tool xero -- invoice list --query where='Status=="AUTHORISED"' --query page=2
heliox tool xero -- invoice get <InvoiceID|InvoiceNumber>
heliox tool xero -- payment list
heliox tool xero -- bank-transaction list
heliox tool xero -- account list          # chart of accounts
heliox tool xero -- item list
heliox tool xero -- tax-rate list
```

`--query key=value` is repeatable and passes straight through as Xero query
parameters (`where`, `order`, `page`, `Statuses`, dates, …).

### Reports

```bash
heliox tool xero -- report pnl --query periods=3
heliox tool xero -- report balance-sheet
heliox tool xero -- report trial-balance
heliox tool xero -- report aged-receivables --query contactId=<ContactID>
heliox tool xero -- report aged-payables --query contactId=<ContactID>
```

### Write

Writes take a raw Xero JSON envelope via `--data` (or `--file <path>`).
**Create** uses PUT; **update** uses POST (Xero's own convention).

```bash
# create an invoice
heliox tool xero -- invoice create --data '{"Invoices":[{"Type":"ACCREC","Contact":{"ContactID":"..."},"LineItems":[...],"Status":"DRAFT"}]}'

# update a contact
heliox tool xero -- contact update --data '{"Contacts":[{"ContactID":"...","EmailAddress":"new@acme.com"}]}'

# record a payment (PUT)
heliox tool xero -- payment create --data '{"Payments":[{"Invoice":{"InvoiceID":"..."},"Account":{"Code":"090"},"Amount":100.0,"Date":"2026-01-31"}]}'

# email a sales invoice to its contact
heliox tool xero -- invoice email <InvoiceID>
```

Write coverage is the high-frequency path: invoices/bills, contacts, payments,
bank transactions, and items.

### Escape hatch: reach any Accounting resource

`fetch` is a raw GET under `api.xro/2.0` for resources the typed subcommands
don't enumerate (quotes, credit notes, manual journals, tracking categories…):

```bash
heliox tool xero -- fetch CreditNotes --query where='Status=="PAID"'
heliox tool xero -- fetch Quotes
```

## Footguns

- **Multi-org "exit 2" is not an error to retry blindly**. Read the candidate
  list it prints and pass the right `--tenant`. Names are matched
  case-insensitively; an ambiguous name also exits 2 (pass the GUID instead).
- **A database *row*-style empty read doesn't apply here**: every list/get
  returns the Xero envelope directly; there is no separate properties call.
- **Errors carry Xero's own body.** With `--json`, failures render as
  `{"error":{"tool":"xero","code":"api_error","status":<http>,"details":<xero body>}}`
  so a `ValidationException` (400) or `Detail` (401/403) is visible, not
  swallowed. Exit codes: 0 success, 1 API/transport failure, 2 usage (bad
  flags, unknown subcommand, ambiguous/unknown tenant).
```
