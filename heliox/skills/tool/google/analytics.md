# Google Analytics (`heliox tool google analytics -- ...`)

Read [google.md](./google.md) first for auth and account selection. Everything
after `--` is the analytics tool's own CLI. This is **GA4, read-only
reporting**: traffic, engagement, conversions, and who's on the site right
now. It cannot create properties, edit config, or send data. Connecting Gmail
does **not** connect Analytics: each Google app is its own connection with its
own consent. If a command reports no connection, run
`heliox tool google auth analytics` and forward the link to the user.

## Always discover the property id first

Every report needs a **numeric GA4 property id**, and the user rarely knows it.
Start here. It lists every account and property the connection can read:

```bash
heliox tool google analytics -- property list --json
```

Each row is `properties/<id>  <name>  (account: ...)`. Use that `<id>` (bare
number or `properties/<id>`, both accepted) as `--property` below.

## Discover valid dimension/metric names: don't guess

GA4 metric and dimension names are exact API strings (`activeUsers`,
`screenPageViews`, `sessionSource`), and a wrong name fails the whole report.
List the valid ones (including a property's custom definitions) before building
a report:

```bash
# All metric + dimension API names for the property
heliox tool google analytics -- report metadata --property 123456 --json

# Narrow to what you need
heliox tool google analytics -- report metadata --property 123456 --kind metrics --search user
```

## Core reporting

```bash
# Traffic last 28 days by channel (default date range is 28daysAgo..today)
heliox tool google analytics -- report run --property 123456 \
  --metrics sessions,activeUsers --dimensions sessionDefaultChannelGroup --json

# Top pages this month, most-viewed first, top 20
heliox tool google analytics -- report run --property 123456 \
  --metrics screenPageViews --dimensions pagePath \
  --start-date 2026-07-01 --end-date today \
  --order-by metric:screenPageViews:desc --limit 20 --json

# Filter to one country (repeatable --filter is ANDed dimension equality)
heliox tool google analytics -- report run --property 123456 \
  --metrics sessions --dimensions city --filter country==United States --json

# Who is on the site right now (last 30 min; 60 for GA 360): use `report realtime`, not `report run`
heliox tool google analytics -- report realtime --property 123456 --metrics activeUsers --json  # realtime totals
heliox tool google analytics -- report realtime --property 123456 \
  --metrics activeUsers --dimensions unifiedScreenName --json  # broken down by screen
```

Dates take **native GA4 forms verbatim**: `YYYY-MM-DD`, `NdaysAgo`,
`yesterday`, `today`. Don't invent a format.

## Filters, ordering, pagination

- `--filter dim==value` (repeatable) is sugar for ANDed exact-match dimension
  filters. For anything richer (OR groups, numeric/`inList`/regex filters), pass
  a raw Data API `FilterExpression` via `--filter-json '<json>'`. The two are
  mutually exclusive.
- `--order-by metric:<name>:desc` or `dimension:<name>:asc` (repeatable;
  direction defaults to `asc`).
- `--limit` / `--offset` paginate. Default output is a compact table; when the
  response has more rows than returned, a `row count: N (returned M; paginate…)`
  line is printed; page with `--offset` to get the rest.

## Output

Default is a human-readable table (dimension columns then metric columns).
Add `--json` to get the raw provider response for exact numbers or further
processing. Always prefer `--json` when you need to compute or compare values.

## Failure notes

- **No connection / connected Gmail but not Analytics** → auth fails; run
  `heliox tool google auth analytics`, forward the link, and remind the user
  that Gmail's authorization does not cover Analytics.
- **Multiple Google accounts** → pass `--account <email>` before `--` to pick
  which connection to use.
- **401 with a scope hint** → the connection is stale/mis-scoped; ask the user
  to disconnect and reconnect (fresh consent re-grants `analytics.readonly`).
- **403 mentioning an API "not enabled" or "has not been used in project"** →
  the OAuth client's Google Cloud project has the Data or Admin API disabled;
  this is a project-config issue on the Helio side, not the user's: surface it,
  don't retry.
- **Invalid metric/dimension name** → the error names the offending field; fix
  it against `report metadata` output rather than guessing again.
