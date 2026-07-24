# Google Ads (`heliox tool google ads -- ...`)

Read [google.md](./google.md) for auth and account selection. Everything after
`--` is the Google Ads tool's own CLI. This tool is **reporting-first**: it runs
GAQL (Google Ads Query Language) and a small set of guarded status/budget
changes — it is a steering wheel, not a campaign builder (no create/delete).

## Start by listing accounts

Every other command needs a `--customer-id`. Get the reachable ones first:

```bash
heliox tool google ads -- accounts list --json    # .data... resourceNames: ["customers/1234567890", ...]
```

Customer ids are digits (hyphens from the UI like `123-456-7890` are accepted and
stripped). Agency / manager (MCC) users add `--login-customer-id <mcc-id>` to
operate through their manager account — it is normalized the same way (hyphens
stripped to the digits-only form the API requires), and a non-numeric value is a
usage error, not a silent provider-side failure.

## Reporting

`report` composes the GAQL for the common "how did X perform" ask; `query` is the
raw escape hatch for anything else.

```bash
# Convenience report (builds the GAQL for you)
heliox tool google ads -- report --customer-id 1234567890 --resource campaign --date-range LAST_30_DAYS --json
heliox tool google ads -- report --customer-id 1234567890 --resource keyword --date-range LAST_7_DAYS \
  --metrics metrics.clicks,metrics.cost_micros,metrics.conversions --json

# Raw GAQL — full power
heliox tool google ads -- query --customer-id 1234567890 \
  --gaql "SELECT campaign.name, metrics.impressions, metrics.clicks FROM campaign WHERE segments.date DURING LAST_7_DAYS" --json
```

- `--resource` is `campaign` | `ad_group` | `keyword`; `--date-range` is a GAQL
  DURING literal (`LAST_7_DAYS`, `LAST_30_DAYS`, `THIS_MONTH`, …). For custom
  windows (`BETWEEN '2026-01-01' AND '2026-01-31'`) use `query`.
- Both `report` and `query --stream` use searchStream and return one flattened
  `results` array — the streamed-array quirk never reaches you.
- **Money is micros**: `metrics.cost_micros` and budget amounts are millionths
  of the account currency (5_000_000 micros = 5.00). Divide by 1,000,000 before
  showing a currency figure to the user.

## Campaigns + guarded writes

```bash
heliox tool google ads -- campaigns list --customer-id 1234567890 --status ENABLED --json
heliox tool google ads -- campaign set-status --customer-id 1234567890 --id 55 --status PAUSED --json
heliox tool google ads -- budget set --customer-id 1234567890 --id 9 --amount-micros 5000000 --json
```

- Writes are explicit-id only and reversible-ish (`set-status` toggles
  ENABLED/PAUSED; no REMOVED). There is **no create or delete** in this tool.
- Spending changes real money. Before a `budget set` or pausing/enabling a
  campaign, confirm the target and the new value with the user — state the human
  figure (e.g. "raise the daily budget to $50 / 50,000,000 micros"), not just
  the micros.

## Failure notes

- Errors surface Google's nested `error.details[].errors[]` verbatim under
  `--json` (`AuthenticationError`, `QueryError`, `QuotaError`, …) — read the
  `errorCode` to know whether to fix the GAQL, back off, or ask the user to
  reconnect.
- A `QUOTA` / daily-limit error usually means the app's developer token is on
  Explorer/Test access (2,880 ops/day) — a workspace-config limit, not
  something you can fix from here; tell the user.
- 401 → reconnect (fresh consent re-grants the `adwords` scope). 403 is usually
  a customer-id the account can't reach, or a missing manager header — recheck
  `accounts list` and `--login-customer-id`.
- GAQL selects fields; it can't compute arbitrary math. Pull the metrics and do
  the arithmetic yourself.
