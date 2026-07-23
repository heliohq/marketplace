# Braintree (`heliox tool braintree`)

Braintree payments operations over the Braintree GraphQL API: search and
inspect transactions, refund / void / reverse them, look up customers and
disputes, and check subscription status. This is an **operational** surface for
a merchant's existing payments — it does **not** create charges (that needs a
client-collected payment method Helio does not hold).

Read `../SKILL.md` first for the connect model and the tool approval gate.

## Connect

Braintree uses an **API key pair**, not OAuth. The user pastes four fields from
their Braintree **Control Panel → Settings → API → API Keys**:

- `merchant_id`
- `public_key`
- `private_key` (secret)
- `environment` — `sandbox` or `production`

```bash
heliox tool braintree auth --json   # mints the connect link; user pastes the four fields
```

Helio verifies the key pair (a `ping`) before storing it, and keys are
**environment-qualified**: the same `merchant_id` can be connected in both
sandbox and production as two separate accounts. Keys are long-lived; revoke
them in the Braintree Control Panel (disconnect in Helio is local-only).

## Commands

All output is JSON with `--json`; list verbs return
`{ "items": [...], "page_info": { "has_next_page": bool, "end_cursor": "..." } }`
— pass `--after <end_cursor>` to page.

```bash
# Health / credential check
heliox tool braintree -- ping

# Transactions
heliox tool braintree -- transaction search --status SETTLED --amount-min 10 --amount-max 100 \
  --created-after 2026-01-01T00:00:00Z --customer-id CUST123 --order-id ORD-9 --first 50
heliox tool braintree -- transaction get <transaction_id>

# Customers, disputes, subscriptions
heliox tool braintree -- customer get <customer_id>
heliox tool braintree -- customer search --email person@example.com
heliox tool braintree -- dispute search --status OPEN --received-after 2026-01-01
heliox tool braintree -- dispute get <dispute_id>
heliox tool braintree -- subscription get <subscription_id>

# Raw READ-ONLY GraphQL escape hatch (mutations are rejected)
heliox tool braintree -- query 'query { ping }'
```

## Money movement — read this before refunding

Three separate verbs move money. The approval gate prompts before each one:

- `transaction refund <id> [--amount X] [--order-id O]` — refunds a **settled**
  transaction (full, or partial with `--amount`).
- `transaction void <id>` — cancels an **unsettled** transaction. It **errors**
  once the transaction has settled and never moves money that already left.
- `transaction reverse <id>` — the universal reversal: it **voids** an unsettled
  transaction but issues a **FULL REFUND** on an already-**settled** one. Reach
  for `reverse` only when you want that behavior; use `void` when you specifically
  mean "cancel only if still unsettled."

`void` and `reverse` are distinct on purpose — `void` never silently refunds a
settled transaction.

## Notes

- GraphQL errors come back as HTTP 200 with an `errors[]` array; the tool
  surfaces the message + error class and exits non-zero.
- The `query` passthrough is **read-only**: any `mutation` is rejected locally
  (exit 2, no request). Use the named `refund` / `void` / `reverse` verbs for
  writes so the approval gate can reason about them.
- The private/public key never appears in output.
