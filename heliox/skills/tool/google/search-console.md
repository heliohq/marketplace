# Google Search Console (`heliox tool google search-console -- ...`)

Read [google.md](./google.md) first for auth and account selection. Everything
after `--` is the search-console tool's own CLI. This tool reads a site's
Google **Search** performance (clicks / impressions / CTR / position), inspects
whether a page is indexed, and manages sitemaps. Connecting another Google app
does **not** connect Search Console: each Google app is its own connection with
its own consent. If a command reports no connection, run
`heliox tool google auth search-console` and forward the link to the user.

## Properties come first

Every other command needs a `--site`, and a property comes in one of two forms.
Pass it **verbatim**, the tool handles escaping:

- URL-prefix: `https://example.com/` (note the trailing slash)
- Domain property: `sc-domain:example.com`

```bash
# Which properties can this account see, and at what access level?
heliox tool google search-console -- sites list --json
heliox tool google search-console -- sites get --site https://example.com/ --json
```

## Search analytics: the core value

```bash
# Last 28 days, top queries (PT dates, inclusive; --days is a convenience window)
heliox tool google search-console -- query --site https://example.com/ \
  --days 28 --dimensions query --json

# Explicit range, broken down by page, top 50 rows
heliox tool google search-console -- query --site https://example.com/ \
  --start 2026-06-01 --end 2026-06-30 --dimensions page --row-limit 50 --json

# Filtered: mobile traffic to /blog pages, by query
heliox tool google search-console -- query --site https://example.com/ \
  --days 28 --dimensions query \
  --filter page:contains:/blog --filter device:equals:MOBILE --json
```

- `--dimensions` (comma-separated): `query`, `page`, `country`, `device`,
  `date`, `hour`, `searchAppearance`. No dimension = site totals.
- `--filter dimension:operator:expression` (repeatable, joined as AND):
  operators are `equals`, `notEquals`, `contains`, `notContains`,
  `includingRegex`, `excludingRegex` (RE2). All filters form one AND group;
  the API supports nothing else.
- `--type`: `web` (default), `image`, `video`, `news`, `discover`, `googleNews`.
- `--data-state final` (default; finalized data) vs `all` (includes fresh,
  still-moving data). `--aggregation`, `--row-limit` (1-25000, default 1000),
  and `--start-row` for paging are also there. Check `-- --help`.
- Response rows carry `keys`, `clicks`, `impressions`, `ctr` (0-1), `position`.
  Data is ~2-3 days behind and covers ~16 months; the top rows only, so totals
  from a paged query undercount the long tail.

## "Is this page indexed, and why not?"

```bash
heliox tool google search-console -- inspect --site https://example.com/ \
  --url https://example.com/new-page --json
```

Returns the **indexed** version's status (coverage verdict, crawl/index state,
mobile-usability, rich-result checks), not a live fetch. Per-property quota is
2000 inspections/day and 600/min; a 429 is Google's quota, surfaced verbatim:
back off, don't hammer.

## Sitemaps

```bash
heliox tool google search-console -- sitemaps list --site https://example.com/ --json
heliox tool google search-console -- sitemaps get  --site https://example.com/ \
  --sitemap https://example.com/sitemap.xml --json

# Submit (or resubmit): the key write action
heliox tool google search-console -- sitemaps submit --site https://example.com/ \
  --sitemap https://example.com/sitemap.xml

# Remove a stale sitemap
heliox tool google search-console -- sitemaps delete --site https://example.com/ \
  --sitemap https://example.com/sitemap.xml
```

`submit` / `delete` return `{"ok":true,...}`: the API sends an empty body, so
confirm success from the exit status, not a payload. Submitting a sitemap tells
Google to (re)crawl it; report the action to the user when it changes their
live property.

## Failure notes

- **No connection / connected another Google app but not Search Console** →
  auth fails; run `heliox tool google auth search-console`, forward the link,
  and remind the user that another Google app's authorization does not cover
  Search Console.
- **Multiple Google accounts** → pass `--account <email>` before `--` to pick
  which connection to use.
- **403 with a scope hint** → the connection predates the `webmasters` scope, or
  the account lacks access to that property; ask the user to disconnect and
  reconnect (fresh consent re-grants everything), and confirm they own/manage
  the property.
- **`sc-domain:` vs URL-prefix mismatch** → a property is one specific form; if
  `sites list` shows `sc-domain:example.com`, querying `https://example.com/`
  will 403/404. Use the exact string from `sites list`.
- **Empty query result** → the window may predate the property's data, or the
  filter excluded everything; widen the range or drop filters to confirm.
