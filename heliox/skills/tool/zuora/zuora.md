# Zuora (`heliox tool zuora -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Zuora is a
**flat provider**: everything after `--` is the Zuora tool's own CLI, speaking
Zuora Billing REST v1 with a bearer the tool mints from the connected account's
OAuth client.

```bash
heliox tool zuora [--account <key>] -- <resource> <verb> [args...]
```

Read `-- <resource> --help` for the full flag surface.

## Connecting (three fields, not a single key)

Zuora has no shared "authorize with Zuora" consent screen. The user creates an
**OAuth client inside their own Zuora tenant** (Administration → user →
*OAuth Clients* → *Create*) and supplies three values at connect time:

- **REST base URL** — the host of their data center / environment. It cannot be
  inferred from the id/secret and must be entered (examples below).
- **Client ID** and **Client Secret** — from the OAuth client they created.

The tool exchanges these for a short-lived bearer per run
(`POST {base_url}/oauth/token`, client-credentials); you never handle the
bearer.

Base URLs by environment:

| Environment | Base URL |
|---|---|
| US Production (Cloud 1 / Cloud 2) | `https://rest.na.zuora.com` / `https://rest.zuora.com` |
| US API Sandbox (Cloud 1 / Cloud 2) | `https://rest.sandbox.na.zuora.com` / `https://rest.apisandbox.zuora.com` |
| EU Production | `https://rest.eu.zuora.com` |
| EU Sandbox | `https://rest.sandbox.eu.zuora.com` |

## Command surface (read-first)

```bash
heliox tool zuora -- account get <account-key>          # balance, currency, bill-to/sold-to
heliox tool zuora -- account summary <account-key>      # rolled-up: subscriptions + recent invoices/payments
heliox tool zuora -- subscription list <account-key>    # all subscriptions for an account
heliox tool zuora -- subscription get <subscription-key> # rate plans, charges, term
heliox tool zuora -- invoice get <invoice-id>           # amount, balance, status, due date
heliox tool zuora -- invoice list <account-key>         # account's invoices (ZOQL under the hood)
heliox tool zuora -- payment get <payment-id>           # one payment (see caveat)
heliox tool zuora -- payment list <account-key>         # account's payments (ZOQL; no Settlement dependency)
heliox tool zuora -- catalog products                   # product catalog + rate plans (cheap smoke read)
heliox tool zuora -- query --zoql "select ... from ..."  # read-only ZOQL escape hatch
```

`account key` and `subscription key` accept either the number
(e.g. `A00000123`) or the internal id. Account keys you pass to `invoice list` /
`payment list` are bound as quoted ZOQL literals — you do not need to quote or
escape them yourself.

## ZOQL — the power tool

`query --zoql` runs a read-only ZOQL `SELECT` over any queryable object
(`Account`, `Subscription`, `Invoice`, `Payment`, `RatePlan`, …). It is the
fallback for anything not first-classed above:

```bash
heliox tool zuora -- query --zoql "select Id, Name, Balance from Account where Status = 'Active'"
```

Only `SELECT` is accepted (the tool refuses write verbs locally).

## Two caveats worth knowing

- **`payment get` / `payment list` (the GET path) need the tenant's Invoice
  Settlement feature** (GA March 2021, not universal). On a tenant without it,
  the direct payment reads error. `payment list` already routes through ZOQL
  over the `Payment` object, which does **not** carry this dependency; for a
  single payment on such a tenant, use `query --zoql "select ... from Payment
  where Id = '...'"`.
- **These are Zuora's legacy v1 Billing APIs**, chosen for stability and
  documentation coverage. Zuora steers new integrations toward Object Query
  (`/object-query/...`); that is the natural future migration target if a v1
  endpoint is deprecated.

## Errors

A non-2xx (or a 2xx body signalling failure) exits non-zero with the Zuora error
message. A 401 is a rejected/expired credential — ask the user to reconnect. A
403 usually means the OAuth client's role lacks access to that object.
