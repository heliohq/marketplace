# DataForSEO (`heliox tool dataforseo -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. DataForSEO is
a **flat provider** (not grouped): everything after `--` is the dataforseo
tool's own CLI.

```bash
heliox tool dataforseo [--account <key>] -- <group> <command> [flags...]
```

DataForSEO is a **metered, pay-per-request SEO data API**: it answers
rank-checking, keyword-research, competitor-research, and backlink questions
without a browser. Use it when the user needs real SERP/keyword/backlink data,
not a general web search.

## Cost: read this first (every call spends real money)

Every command except `account` and `meta` is **charged per request** (fractions
of a cent to a couple of cents each). Every success prints a `cost` field (USD)
in its output. Check it. Two rules:

- **Check funds before a large job.** `account` is free and shows the balance:
  `heliox tool dataforseo -- account`. If `result[0].money.balance` is low, tell
  the user to top up at app.dataforseo.com rather than burning failed calls.
- **A `serp google` keyword using an operator (`site:`, `inurl:`, …) costs ~5x**
  a plain keyword. Only add operators when the question needs them.

Errors are explicit: an out-of-balance call fails with an "insufficient
DataForSEO balance" message (not a silent empty result); a rejected credential
tells the user to reconnect.

## Output shape

Every command prints one JSON object: `{"cost": <usd>, "result": [...]}`.
`result` is the unwrapped data array (the DataForSEO `version`/`tasks` envelope
is stripped). `result` may be `null` when a query legitimately matches nothing.

## Location & language (the #1 friction)

Most commands accept `--location` (default `"United States"`) and `--language`
(default `en`). `--location` takes either a **name** (`"United Kingdom"`) or a
numeric **location_code** (`2840`). When unsure of the exact name/code, look it
up first (free-of-charge-shaped reference lists):

```bash
heliox tool dataforseo -- meta locations --search "united"
heliox tool dataforseo -- meta languages --search "span"
```

## Commands

### Rank checking (SERP)

```bash
# live Google organic SERP for a keyword
heliox tool dataforseo -- serp google --keyword "best crm software" \
  [--location "United States"] [--language en] [--depth 20] [--device desktop|mobile]
```

### Keyword research

```bash
heliox tool dataforseo -- keywords volume       --keywords "seo,ppc,link building"   # Google Ads search volume
heliox tool dataforseo -- keywords ideas        --keywords "crm" [--limit 100]        # related ideas (broad)
heliox tool dataforseo -- keywords suggestions  --keyword  "crm" [--limit 100]        # long-tail (single seed)
heliox tool dataforseo -- keywords difficulty   --keywords "crm,helpdesk"             # difficulty scores
heliox tool dataforseo -- keywords intent       --keywords "buy crm,what is crm" --language en   # search intent (no location)
```

### Domain & competitor research

```bash
heliox tool dataforseo -- domain overview        --target example.com                 # organic/paid visibility
heliox tool dataforseo -- domain ranked-keywords --target example.com [--limit 100]   # keywords it ranks for
heliox tool dataforseo -- domain competitors     --target example.com [--limit 100]   # SERP competitors
```

`--target` is a bare domain (`example.com`, no `https://`/`www.`) for
domain-level data, or a full `https://…` URL for page-level data.

### Backlinks

```bash
heliox tool dataforseo -- backlinks summary           --target example.com            # aggregate metrics
heliox tool dataforseo -- backlinks list              --target example.com [--limit 100]
heliox tool dataforseo -- backlinks referring-domains --target example.com [--limit 100]
heliox tool dataforseo -- backlinks anchors           --target example.com [--limit 100]
```

### On-page & account

```bash
heliox tool dataforseo -- onpage check --url https://example.com/pricing   # instant single-page audit
heliox tool dataforseo -- account                                          # balance, limits, pricing (free)
```

## Connecting

DataForSEO uses an **API login + API password** (HTTP Basic auth, not OAuth),
both shown at app.dataforseo.com/api-access. Note the API password is
auto-generated and differs from the account password. The user pastes them as a
single `login:password` pair in the connect form. To rotate, they regenerate the
API password in the dashboard and reconnect.

## Notes

- The tool wraps **Live** (synchronous) endpoints only: one request, one
  response. Task-queue and site-crawl modes are intentionally not exposed.
- Prefer `meta locations`/`meta languages` over guessing identifiers; a wrong
  location still costs money and returns the wrong market's data.
