# Recurly (`heliox tool recurly -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Recurly is a
**flat provider** (not grouped like `google`): everything after `--` is the
recurly tool's own CLI.

```bash
heliox tool recurly [--account <key>] -- <resource> <verb> [flags...]
```

Recurly is a subscription-billing / recurring-revenue platform. The tool wraps
the **Recurly V3 REST API** (version `v2021-02-25`). It is **read-first**: the
common jobs are looking up a customer and their subscription state, explaining
a failed or past-due invoice, and listing plans/coupons, plus a curated set of
subscription and invoice lifecycle writes.

Connect once (`heliox tool recurly auth`), then the user pastes their Recurly
**private API key** (Integrations → API Credentials in their Recurly site). The
key is stored server-side and injected per call. You never see it. The
connection is verified against `GET /sites` and labeled by the site subdomain.

> Region: this connection targets the **US** data center (`v3.recurly.com`). An
> EU-only Recurly site is not supported yet: its key will fail to connect.

## Addressing objects (alias prefixes)

Recurly IDs are opaque (e.g. `e28zov4fw0v2`), but every id argument also accepts
a human-friendly alias so you rarely need a prior lookup:

- `code-<account_code>`: an account by its business code, e.g. `code-bob`
- `number-<invoice_number>`: an invoice by its number, e.g. `number-1000`
- `uuid-<subscription_uuid>`: a subscription by its UUID, e.g. `uuid-abc123`

Pass these verbatim wherever an `<id>` is expected.

## Command tree

```
recurly account      list | get <id> | balance <id> | billing-info <id>
recurly subscription list | get <id> | create | change <id> | cancel <id> | pause <id> | resume <id> | terminate <id>
recurly invoice      list | get <id> | line-items <id> | collect <id>
recurly transaction  list | get <id>
recurly plan         list | get <id>
recurly coupon       list | get <id>
recurly line-item    list
recurly site         list
```

Every leaf takes `--json`. `list` leaves accept `--limit`, `--cursor` (feed
back a prior response's `next`), `--state`, `--type`, `--order`, `--sort`,
`--begin-time` / `--end-time`. Account-scoped lists (`subscription`, `invoice`,
`transaction`, `line-item`) accept `--account code-<code>` to scope to one
customer.

## Common workflows

```bash
# Who is this customer and what is their subscription state?
heliox tool recurly -- account get code-bob --json
heliox tool recurly -- subscription list --account code-bob --json

# Why is this invoice failing / is the account past due?
heliox tool recurly -- invoice get number-1000 --json
heliox tool recurly -- invoice line-items number-1000 --json
heliox tool recurly -- transaction list --account code-bob --json

# What plans / coupons exist?
heliox tool recurly -- plan list --json
heliox tool recurly -- coupon list --json
```

## Lifecycle writes (use deliberately: these change billing state)

```bash
# Cancel at period end (vs terminate = end now)
heliox tool recurly -- subscription cancel uuid-abc123 --json

# Pause for N future billing cycles, then resume
heliox tool recurly -- subscription pause uuid-abc123 --cycles 2 --json
heliox tool recurly -- subscription resume uuid-abc123 --json

# Terminate now, optionally refunding: none | partial | full
heliox tool recurly -- subscription terminate uuid-abc123 --refund none --json

# Retry collection on a failed invoice
heliox tool recurly -- invoice collect number-1000 --json

# Create / change take a raw Recurly JSON body
heliox tool recurly -- subscription create --body '{"plan_code":"gold","currency":"USD","account":{"code":"bob"}}' --json
heliox tool recurly -- subscription change uuid-abc123 --body '{"plan_code":"silver"}' --json
```

Payment mutations (refunds beyond `terminate --refund`, account redaction /
GDPR) are intentionally **not** exposed: they are high-blast-radius financial
writes a teammate should not reach for by default.

## Output & errors

`get` passes the Recurly resource JSON through unchanged. `list` returns a
provider-neutral envelope: `{ "data": [...], "has_more": <bool>, "next":
"<cursor>" }`. Page by re-running with `--cursor <next>` until `has_more` is
false. Exit codes: `0` success, `1` API/runtime error (Recurly's typed
`{error:{type,message}}` is surfaced; a `429` echoes `Retry-After`), `2`
usage/parse error (bad flag, invalid `--body` JSON).
