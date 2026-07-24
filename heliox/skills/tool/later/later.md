# Later (Influence Reporting)

`heliox tool later` reads **Later Influence** creator/social campaign
performance through the Later Influence Reporting API (v2). Read the tool model
in [../SKILL.md](../SKILL.md) first.

## What this is — and is NOT

- **Is**: read-only analytics — pull campaign and instance (workspace)
  performance for reporting.
- **Is NOT**: social scheduling or publishing. Later's post-scheduling product
  has **no public API**. Do not attempt to schedule, publish, or edit posts
  through this tool — there is no such command, and none can be added.

## Connect

Later Influence Reporting API credentials are a **clientId / clientSecret**
pair, issued only by a Later account team (not self-serve). The user pastes them
in the connect drawer as a single `clientId:clientSecret` value; Helio verifies
the pair and stores it. If `heliox tool list` shows no `later` row, ask the user
to connect it and relay the auth link — you cannot authorize on their behalf.

## Commands

Everything after `--` goes to the tool. Both commands are read-only GETs.

```bash
# List the reporting instances (workspaces) the credential can see.
heliox tool later -- instances --json [--limit <1-100>]

# Read campaign performance over a date range (UTC YYYY-MM-DD, required).
heliox tool later -- campaigns --json \
  --start 2025-01-01 --end 2025-01-31 \
  [--metrics engagements,impressions] \
  [--instance-ids <id,id>] [--campaign-ids <id,id>] \
  [--platform instagram|tiktok|youtube|facebook|...] \
  [--content-type instagram_reel|...] \
  [--date-basis post_date|performance_date] \
  [--sort <property> --sort-dir ASC|DESC] \
  [--limit <1-100>] [--cursor <nextCursor>]
```

Notes:

- Run `instances` first when you need `--instance-ids`; omit `--instance-ids`
  to span every instance the credential can access.
- `--start` and `--end` are required on `campaigns` (max two-year span).
- Paginate with `--cursor`: pass the `nextCursor` from the previous response
  until it comes back `null`.
- Organic metrics use plain names (`impressions`, `engagements`); paid metrics
  carry a `paid` prefix (`paidImpressions`, `paidEngagementRate`).

## Errors

- `401 reconnect required` — the clientId/clientSecret no longer authorizes;
  ask the user to reconnect.
- `403` — the credential lacks access to the requested instance/scope; it does
  not mean the credential is invalid.
