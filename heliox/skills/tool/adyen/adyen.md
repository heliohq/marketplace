# Adyen (`heliox tool adyen -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Adyen is a
**flat provider** (not grouped like `google`): everything after `--` is the
adyen tool's own CLI.

```bash
heliox tool adyen [--account <key>] -- management <resource> <verb> [flags...]
```

## What this tool is (and is NOT) today

v1 wraps the **Adyen Management API v3** only, and it is **read/config
introspection** — it inspects accounts, payment-method configuration, webhooks,
stores, and terminals. Three hard limits to set expectations before you reach
for it:

- **It moves no money.** There is no charge, no refund, no capture, no payment
  link. Those are Checkout operations and are a **v2** capability that is **not
  available yet**. If a task needs to request or move money, this tool cannot do
  it — say so rather than improvising.
- **It is live-only.** A connected Adyen credential is always a **live** key, so
  every command runs against the live Adyen account. There is no test/sandbox
  switch on the connected tool.
- **There is no "list all recent payments" call.** Adyen has no simple REST
  endpoint that lists transactions for a classic merchant — reconciliation is
  webhook- and downloadable-report-driven. Work from a known `pspReference` (from
  a webhook or the Customer Area), never expect to enumerate payments here.

## Commands (all read-only GETs)

```bash
# Who is this key? (also the connect verifier target)
heliox tool adyen -- management whoami --json

# Merchant + company accounts
heliox tool adyen -- management merchant list [--page-size N] [--page N] --json
heliox tool adyen -- management merchant get <merchantId> --json
heliox tool adyen -- management company list [--page-size N] [--page N] --json
heliox tool adyen -- management company get <companyId> --json

# Payment-method settings enabled on a merchant
heliox tool adyen -- management payment-methods list <merchantId> --json

# Webhooks — pass exactly one scope: --merchant OR --company
heliox tool adyen -- management webhook list --merchant <merchantId> --json
heliox tool adyen -- management webhook list --company <companyId> --json
heliox tool adyen -- management webhook get  --merchant <merchantId> <webhookId> --json

# In-person estate
heliox tool adyen -- management store list <merchantId> --json
heliox tool adyen -- management terminal list [--merchant <merchantId>] --json
```

Output is Adyen's JSON verbatim. List endpoints wrap results in a `data` array
with `itemsTotal` / `pagesTotal`; pagination is `--page-size` (max 100) and
`--page` (1-based). `terminal list` hits Adyen's **top-level** terminals
endpoint filtered by `--merchant`, so it can also list every terminal the key
can see when no merchant is given.

## The role gotcha (read this before you blame the key)

Adyen Management API keys carry **granular per-endpoint roles**. `whoami`
(`GET /me`) succeeds with *any* Management role, so a key can connect
successfully and still lack the role a later command needs.

- **A `403` means "the key is missing a role", NOT "reconnect".** The tool
  surfaces Adyen's `errorCode` (typically `010`) and message and exits non-zero;
  it is **not** a credential rejection. The fix is to **add the missing role in
  the Adyen Customer Area** (Developers → API credentials → the key → Roles),
  then retry the *same* connection. Do not send the user a reconnect link for a
  403 — a fresh key with the same roles will 403 identically.
- **A `401` is a real auth failure** (missing/incorrect key) and does mark the
  connection for reconnect — ask the user to reconnect with a valid key.

For the v1 command set the key should carry all of these Management API read
roles so it won't 403 mid-use: **Accounts read** (whoami / merchant / company),
**Payment methods read**, **Webhooks read**, **Stores read**, and **Terminals
read**. When Checkout lands in v2 the key additionally needs the **Checkout API**
role.

## Setup

The user creates the key in **Customer Area → Developers → API credentials**,
grants it the read roles above, and pastes it into the Helio connect drawer
(stored encrypted; you never see it). Adyen keys are long-lived and
non-expiring — they are rotated or revoked manually in the Customer Area.
