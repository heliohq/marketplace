# Sage Accounting (`heliox tool sage -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Sage is a
**flat provider** (not grouped like `google`): everything after `--` is the
sage tool's own CLI, wrapping the **Sage Accounting API v3.1**
(`api.accounting.sage.com/v3.1`).

```bash
heliox tool sage [--account <key>] -- [--business <id>] <resource> <verb> [flags...]
```

The surface is **read-first**: list/get on every resource, plus a few explicit
writes (`contact create`, `sales-invoice create`, `contact-payment create`).
All output is Sage's own JSON, verbatim.

## The mental model (read this first)

- **Business scoping is per call, not per connection.** One Sage connection can
  reach every business the authorizing user can access. Pick which one with the
  global `--business <id>` flag; omit it and Sage uses the user's **lead
  business**. Discover the ids with `business list` and pass the one you want on
  every subsequent call.
- **List responses are Sage's paginated envelope** — `$items`, `$total`,
  `$page`, `$next`. There is no `--all`: page through with `--page` /
  `--items-per-page` and continue while `$next` is present.
- **Writes take a verbatim `--body` JSON envelope** — you supply the exact Sage
  resource object (with its root key), because the accounting schema is
  country-variable (UK VAT vs US sales tax vs FR TVA) and high-stakes. There
  are no per-field flags for writes.

## Core commands

### Read

```bash
# discover businesses (the ids you pass to --business)
heliox tool sage -- business list
heliox tool sage -- business get <business-id>

# customers & suppliers
heliox tool sage -- --business <id> contact list --items-per-page 50
heliox tool sage -- --business <id> contact get <contact-id>

# sales invoices (customer) and purchase invoices (supplier bills)
heliox tool sage -- --business <id> sales-invoice list --page 1
heliox tool sage -- --business <id> sales-invoice get <invoice-id>
heliox tool sage -- --business <id> purchase-invoice list
heliox tool sage -- --business <id> purchase-invoice get <invoice-id>

# financial context
heliox tool sage -- --business <id> ledger-account list      # chart of accounts
heliox tool sage -- --business <id> bank-account list        # balances / cash
heliox tool sage -- --business <id> tax-rate list            # correct tax for new invoices
heliox tool sage -- --business <id> product list
heliox tool sage -- --business <id> service list
```

### Write (each is an explicit verb; the AI builds the envelope)

```bash
# create a contact — body wraps a `contact` object
heliox tool sage -- --business <id> contact create --body \
  '{"contact":{"name":"Acme Ltd","contact_type_ids":["CUSTOMER"],"main_address":{...}}}'

# raise a sales invoice — body wraps a `sales_invoice` object
heliox tool sage -- --business <id> sales-invoice create --body \
  '{"sales_invoice":{"contact_id":"<id>","date":"2026-07-23","invoice_lines":[...]}}'

# record a payment/receipt against an invoice — body wraps a `contact_payment`
# object; allocate against an invoice via allocated_artefacts[].artefact_id
heliox tool sage -- --business <id> contact-payment create --body \
  '{"contact_payment":{"transaction_type_id":"CUSTOMER_RECEIPT","contact_id":"<id>","bank_account_id":"<id>","date":"2026-07-23","total_amount":240,"allocated_artefacts":[{"artefact_id":"<invoice-id>","amount":240}]}}'
```

Payments (both customer receipts and supplier payments) go through
`contact-payment create` → `POST /contact_payments`, **not** a per-invoice
endpoint. Set `transaction_type_id` to `CUSTOMER_RECEIPT` or the supplier-payment
type as appropriate.

### Escape hatch — any other v3.1 resource

```bash
heliox tool sage -- --business <id> fetch --method GET --path /journals
heliox tool sage -- --business <id> fetch --method POST --path /addresses --body '{"address":{...}}'
```

`fetch` reaches the ~40 other v3.1 resources not modeled above, on the same
Bearer + `--business` path.

## Footguns

- **Wrong business, silent write.** Omitting `--business` writes to the user's
  lead business. For any create, discover the id with `business list` and pass
  `--business` explicitly so an invoice/payment never lands on the wrong ledger.
- **Invoices post unpaid.** Creating a `sales_invoice` posts against a holding
  account; recording the money is a separate `contact-payment create` that
  allocates against the invoice.
- **Rate limits.** ~100 req/min and ~2,500 req/day per business. A `429` is a
  retryable runtime error (exit 1), not a loop-forever signal — back off.

## Approval gate

Creating invoices, recording payments and creating contacts are outward /
high-impact side effects and may be policy-gated — if a command exits with
`APPROVAL_REQUIRED`, follow the printed steps (see [../SKILL.md](../SKILL.md)
"Approval gate"). Do not pre-confirm in chat; the gate routes the decision to
the human who authorized the Sage account.
