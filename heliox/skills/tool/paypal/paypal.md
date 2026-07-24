# PayPal (`heliox tool paypal -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. PayPal is a
**flat provider** (not grouped like `google`): everything after `--` is the
paypal tool's own CLI.

```bash
heliox tool paypal [--account <key>] -- <resource> <verb> [flags...]
```

Use it as a **finance/ops colleague**: reconcile money coming in (transactions,
balances) and chase receivables (invoices). It is **read-first**: the only write
verbs are drafting and sending invoices. It moves **no money** — no captures,
refunds, or payouts (see Safety).

## Connect (what the user pastes)

PayPal has no "sign in with PayPal" consent screen for this. The user creates a
**REST app** in the PayPal Developer Dashboard and pastes three fields into the
connect form:

- **environment** — `live` or `sandbox`. A Sandbox app's credentials only work
  against sandbox and a Live app's only against live, so this is part of the
  connection's identity, not a per-call flag.
- **client_id** and **client secret** — from that same REST app.

If a command later fails auth, the pair is wrong or belongs to the other
environment — ask the user to reconnect with the matching app.

## Core commands

### Receivables — invoices

```bash
# list invoices (primary receivables view); page 1-1000, page-size 1-100
heliox tool paypal -- invoice list --page 1 --page-size 20 --json

# one invoice's full detail + status
heliox tool paypal -- invoice get <invoice-id> --json

# filter invoices by status / recipient / date range / amount
heliox tool paypal -- invoice search --status UNPAID --recipient-email a@b.com --json
heliox tool paypal -- invoice search --start-date 2026-01-01 --end-date 2026-03-31 --json
```

### Reconciliation — transactions and balances

```bash
# transaction history — window is REQUIRED and must be <= 31 days, RFC3339 dates
heliox tool paypal -- transaction list --start-date 2026-07-01T00:00:00Z --end-date 2026-07-15T00:00:00Z --json

# account balances snapshot (default: now)
heliox tool paypal -- balance list --json
heliox tool paypal -- balance list --as-of-time 2026-07-01T00:00:00Z --json
```

### Subscriptions

```bash
# look up a customer's subscription status (read-only)
heliox tool paypal -- subscription get <subscription-id> --json
```

### Sending an invoice (draft first, then send)

Sending is a two-step, human-visible flow — a draft is **inert** until you
explicitly send it:

```bash
# 1) create a DRAFT — not visible to the recipient, nothing is emailed
heliox tool paypal -- invoice create-draft --body '<PayPal Invoicing v2 create JSON>' --json

# 2) send the drafted invoice (emails the recipient by default)
heliox tool paypal -- invoice send <invoice-id> --note "Thanks!" --json
```

`invoice send` emails a real customer, so it is behind the **approval gate**
(see ../SKILL.md): it exits `APPROVAL_REQUIRED` and prints the exact
`heliox approval request …` next step — follow it, do not pre-confirm in chat.

## Output shape

List verbs emit `{ "results": [ … ], "page": N, "total_pages": N,
"total_items": N }`; single-object verbs emit the object directly. Pass
`--json` for structured output. Page through with `--page` / `--page-size`.

## Footguns

- **Transaction window is capped at 31 days** and dates are RFC3339. Asking for
  a wider range fails — split it into <=31-day windows and page each. History
  reaches back ~3 years.
- **A 403 usually means a feature is not enabled, not a bad token.** Transaction
  Search and Invoicing must be turned on **for the REST app** *and* the PayPal
  account. A fully-valid credential still 403s on `transaction list` until
  `https://uri.paypal.com/services/reporting/search/read` is granted — tell the
  user to enable Transaction Search / Invoicing on the app, don't retry.
- **Wrong environment reads as "no data" or auth failure.** If the user
  connected a Sandbox app, live invoices/transactions simply aren't there.
- **`invoice search` is a distinct endpoint**, not a filtered `invoice list` —
  just use the verb; the tool routes it correctly.

## Safety

- **No money movement.** This tool deliberately cannot capture payments, issue
  refunds, send payouts, or cancel/delete invoices — one malformed argument on
  those is an irreversible transfer. If the user asks to move or reverse money,
  say it is out of scope for the PayPal tool and stop.
- **`invoice send` is the one outward-facing action** and is approval-gated;
  the approval card is the human check — don't also ask for a chat confirmation.
- Never echo the client secret; the CLI never shows credential payloads to you.
