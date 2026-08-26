# Razorpay (`heliox tool razorpay -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Razorpay is a
**flat provider** (not grouped like `google`): everything after `--` is the
razorpay tool's own CLI. It wraps the Razorpay REST API so you can act as a
finance / revenue-ops / support colleague on a connected merchant's account.

```bash
heliox tool razorpay [--account <key>] -- <resource> <verb> [flags...]
```

Output is always the provider's JSON, passed through verbatim (including the
`{"entity":"collection","count":N,"items":[...]}` list envelope). Every command
accepts `--json` (accepted for uniformity; output is JSON regardless).

## Resources

Each resource exposes `list` (paginated) and `get <id>`:

| Resource | Commands | What it is |
|---|---|---|
| `payment` | `list`, `get <pay_id>` | Captured/attempted payments |
| `order` | `list`, `get <order_id>` | Orders (the intent a payment fulfils) |
| `refund` | `list`, `get <rfnd_id>` | Refunds against payments |
| `customer` | `list`, `get <cust_id>` | Saved customers |
| `payment-link` | `list`, `get <plink_id>` | Hosted payment links |
| `settlement` | `list`, `get <setl_id>` | Payouts of collected funds to the merchant bank |
| `subscription` | `list`, `get <sub_id>` | Recurring subscriptions |

```bash
# recent payments
heliox tool razorpay -- payment list --count 10

# one payment by id
heliox tool razorpay -- payment get pay_ABC123

# refunds in a time window (Unix seconds)
heliox tool razorpay -- refund list --from 1700000000 --to 1701000000

# when is the next settlement / what settled
heliox tool razorpay -- settlement list --count 5
```

## Pagination & time windows

Every `list` accepts `--count` (max 100), `--skip` (offset), and optional
`--from` / `--to` (Unix-second bounds). Flags are sent only when you set them,
so Razorpay applies its own defaults otherwise. Page by increasing `--skip` by
your `--count` until `items` comes back short.

## Amounts

Amounts are in the **smallest currency unit** (paise for INR, ₹100 is
`amount: 10000`). The tool passes them through unchanged; never assume rupees.

## Scope of this tool (read before you try a write)

This tool ships **read-only** for the gateway domain: there is no
`create`/`capture`/`refund create` verb yet. Money-moving writes are deferred to
a dedicated pass because Razorpay moves real funds. If the user asks you to
issue a refund or send a payment link, tell them the create verbs are not
enabled yet rather than improvising. RazorpayX banking (payouts / contacts /
fund accounts) is a separate, higher-risk scope family and is out of scope here.

## Errors & exit codes

- Exit **0**: success (JSON on stdout).
- Exit **1**. Razorpay API/runtime failure; stderr carries the provider error
  (`CODE: description`). A `401` means the connection needs reconnecting.
- Exit **2**: usage error (bad flag, missing id).
