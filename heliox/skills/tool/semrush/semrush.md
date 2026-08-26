# Semrush (`heliox tool semrush -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Semrush is a
**flat provider** (not grouped like `google`): everything after `--` is the
semrush tool's own CLI.

```bash
heliox tool semrush [--account <key>] -- <group> <verb> <subject> [flags...]
```

Semrush is competitive **SEO research** over the v3 API: what a domain ranks
for, its estimated organic/paid traffic, keyword metrics (volume / CPC /
difficulty / related / questions), and backlink profiles. Connect with a
Semrush **v3 API key** (Subscription info → API units; needs a Business plan
plus the paid API-units add-on).

## Unit economics: read this before large pulls

**Every returned line costs API units** and they come out of one shared account
balance. Costs run 10-50 units/line depending on the report. To protect the
balance:

- Every report defaults to `--limit 10` (Semrush's own server default is
  10,000 lines). Only raise `--limit` when you deliberately need more rows.
- Check the balance first. It is free (0 units):

  ```bash
  heliox tool semrush -- units --json
  ```

- Prefer the cheaper overview reports before pulling large keyword/backlink
  lists. `keyword difficulty` (50 units/line) and `keyword related` /
  `keyword questions` (40 units/line) are the expensive ones.

## Output shape

Semrush returns semicolon-CSV; the tool parses it into JSON rows keyed by
snake_cased header names (numbers are coerced to numbers):

```json
{"report": "domain_organic", "database": "us", "row_count": 2,
 "rows": [{"keyword": "seo tools", "position": 3, "search_volume": 74000, "cpc": 1.5}]}
```

A query with no data returns `row_count: 0`, an empty `rows` array, and a
`note`. That is a valid answer, not an error.

## Core commands

```bash
# Domain overview + traffic (one regional database, default us)
heliox tool semrush -- domain overview example.com --json
heliox tool semrush -- domain overview example.com --all-databases --json

# What a domain ranks for organically / buys in paid search
heliox tool semrush -- domain organic example.com --limit 25 --json
heliox tool semrush -- domain paid example.com --json

# Competing domains (organic, or --paid for the ad-competition variant)
heliox tool semrush -- domain competitors example.com --json
heliox tool semrush -- domain competitors example.com --paid --json

# Keyword research
heliox tool semrush -- keyword overview "seo tools" --json
heliox tool semrush -- keyword batch "seo tools" "keyword research" --database us --json
heliox tool semrush -- keyword related "seo tools" --json
heliox tool semrush -- keyword questions "seo tools" --json
heliox tool semrush -- keyword difficulty "seo tools" "link building" --json

# Per-URL keywords
heliox tool semrush -- url organic https://example.com/pricing --json

# Backlinks (global, no database; --target-type root_domain|domain|url)
heliox tool semrush -- backlinks overview example.com --json
heliox tool semrush -- backlinks refdomains example.com --limit 50 --json
heliox tool semrush -- backlinks list https://example.com/ --target-type url --json
```

## Shared flags

- `--database` (default `us`): regional database (`us|uk|de|…`). Not used by
  `--all-databases` overviews or backlinks reports (those are global).
- `--limit` / `--offset`: `display_limit` / `display_offset`. Mind the units.
- `--columns`: override `export_columns` (comma-separated Semrush column codes).
- `--filter` / `--sort` / `--date`: `display_filter` / `display_sort` /
  `display_date` passthrough.
- `--positions new|lost|rise|fall`: for change reports.
- `--target-type root_domain|domain|url`: backlinks subject granularity.

## Footguns

- **Version-scoped keys.** This tool speaks the **v3** API only. A v4 key will
  be rejected (`ERROR 120`); paste your v3 key from Subscription info.
- **Zero balance / no API add-on.** `ERROR 132` (units exhausted) or `ERROR
  130` (API not enabled for the plan) mean the account, not the query, is the
  problem: check `units` and the subscription.
- **`domain overview` vs `--all-databases`.** The default is one database
  (`domain_rank`); `--all-databases` aggregates every regional database
  (`domain_ranks`) and omits the `database` field.
