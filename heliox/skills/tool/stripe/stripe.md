# Stripe (`heliox tool stripe -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Stripe is a
**flat provider** (not grouped like `google`): everything after `--` is the
stripe tool's own CLI.

```bash
heliox tool stripe [--account <key>] -- <resource> <verb> [flags...]
```

You are a **finance / revenue-ops / support colleague**, not a checkout
integration. This tool is **read-mostly**: reporting plus a few well-scoped
support mutations (issue a refund, draft/send an invoice, cancel a
subscription). It does not confirm PaymentIntents, tokenize cards, or touch the
webhook event bus — those are customer/edge concerns.

`--account <key>` is a Stripe connected-account id (`acct_***`); omit it when
only one Stripe account is connected.

## Conventions (apply to every command)

- Every response is Stripe's JSON, emitted verbatim on stdout.
- **List pagination** is cursor-based: `--limit <1-100>`, `--starting-after
  <id>`, `--ending-before <id>`. A list response is
  `{"object":"list","data":[...],"has_more":true|false}` — page with the last
  item's id via `--starting-after` while `has_more` is true.
- **Filters** on any list use repeatable `--param key=value` (e.g. `--param
  customer=cus_123`), mapped 1:1 to Stripe's query params.
- **Mutations** take request fields as repeatable `--param key=value`, which map
  1:1 onto Stripe's form fields — bracket notation passes through
  (`--param metadata[order]=A17`). Add `--idempotency-key <k>` on create/refund
  for safe retries.
- **Amounts are in the smallest currency unit** (cents): `--param amount=500` is
  $5.00.
- Exit codes: `0` ok, `1` API/runtime error (Stripe's typed
  `error.{type,code,message}` on stderr; `--json` wraps it as
  `{"error":{message,kind:"api",status}}`), `2` usage error.

## Read (the bulk of the job)

```bash
# account money
heliox tool stripe -- balance get
heliox tool stripe -- balance transactions --limit 20

# payments
heliox tool stripe -- charge list --param customer=cus_123 --limit 10
heliox tool stripe -- charge get ch_123
heliox tool stripe -- payment-intent list          # read-only (no confirm/capture)

# customers, subscriptions, invoices, catalog
heliox tool stripe -- customer get cus_123
heliox tool stripe -- subscription list --param customer=cus_123
heliox tool stripe -- invoice get in_123
heliox tool stripe -- product list
heliox tool stripe -- price list

# settlement, disputes, audit
heliox tool stripe -- payout list
heliox tool stripe -- dispute list
heliox tool stripe -- event list                   # "what changed" audit trail
```

### Search (Stripe Search Query Language)

```bash
heliox tool stripe -- customer search --query "email:'a@b.com'"
heliox tool stripe -- search --resource charges --query "amount>1000 AND status:'succeeded'"
```
`search --resource` accepts: `customers`, `charges`, `invoices`,
`subscriptions`, `prices`. Page a search with `--page <next_page>` from the
prior result.

### Raw GET passthrough

For any long-tail read without a dedicated verb:
```bash
heliox tool stripe -- get account            # GET /v1/account
heliox tool stripe -- get charges --param limit=3
```
The path may be given with or without the `/v1` prefix.

## Support mutations (use deliberately — real money moves)

```bash
# refund a charge (top support action)
heliox tool stripe -- refund create --param charge=ch_123 --idempotency-key r-ch_123
heliox tool stripe -- refund create --param payment_intent=pi_123 --param amount=500   # partial

# customer maintenance
heliox tool stripe -- customer create --param email=a@b.com --param name=Acme
heliox tool stripe -- customer update cus_123 --param metadata[tier]=gold

# invoice lifecycle: create draft → finalize → send
heliox tool stripe -- invoice create --param customer=cus_123
heliox tool stripe -- invoice finalize in_123
heliox tool stripe -- invoice send in_123

# cancel a subscription
heliox tool stripe -- subscription cancel sub_123
```

## Footguns

- **`amount` is in cents.** `--param amount=5` refunds $0.05, not $5.
- **A refund is irreversible.** Confirm the charge/PI id (and the amount for a
  partial refund) before running `refund create`.
- **`payment-intent` and `charge` are read-only here** — this tool never
  confirms or captures a payment.
- **Set `--idempotency-key` on every create/refund** you might retry: a repeat
  without it can double-charge/double-refund.
- **Cursor, not offset.** To walk a large list, follow `has_more` with
  `--starting-after <last id>`; there is no page-number.
