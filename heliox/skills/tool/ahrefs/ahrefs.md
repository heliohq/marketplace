# Ahrefs (`heliox tool ahrefs -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Ahrefs is a
**flat provider** (not grouped like `google`): everything after `--` is the
ahrefs tool's own CLI. Every command here is **read-only**: SEO data in, no
writes. (The credential itself is broader than this command surface; see
[Connect notes](#connect-notes).) Auth is an Ahrefs API v3 key the user
supplies; the tool injects the `Authorization: Bearer` header for you.

```bash
heliox tool ahrefs [--account <key>] -- <group> <verb> [flags...]
```

Every command prints the provider's JSON on stdout. Use it to answer: how
strong is a domain, who links to it, what does it rank for, is a keyword worth
targeting, who ranks for it, and how to compare a set of domains.

## Cost model (read this first: it is the #1 footgun)

Ahrefs bills **API units per (rows × fields)**, minimum 50 units per paid
request, and the units come out of the *connected user's* balance. So:

- Every rows command already defaults to a **curated `--select`** (only the
  fields an agent usually reads) and **`--limit 10`**. Don't widen `--select`
  or raise `--limit` unless you actually need more: each extra field/row costs
  units.
- `usage` is **free** (0 units). Run it first to see the plan and remaining
  units; it also doubles as the "is this connected and working?" probe.
- `batch` compares up to 100 targets in **one** request, far cheaper than
  looping per-domain.

## Commands

```bash
# FREE: plan, unit limits/usage, reset date (also the health check)
heliox tool ahrefs -- usage --json

# Domain strength: merges domain-rating + backlinks-stats + metrics into one object
heliox tool ahrefs -- domain overview --target ahrefs.com [--date YYYY-MM-DD] [--cheap]
#   --cheap = domain-rating only (skip the two extra calls); --date defaults to today UTC

# Backlinks
heliox tool ahrefs -- backlinks list   --target example.com [--limit N] [--where '<expr>'] [--order-by 'traffic:desc'] [--mode domain] [--protocol https]
heliox tool ahrefs -- backlinks broken --target example.com [...same row flags]
heliox tool ahrefs -- refdomains       --target example.com [...same row flags]   # cheaper "who links to us"

# What a site ranks for / its best pages / its competitors
heliox tool ahrefs -- keywords organic --target example.com [--country us] [--date YYYY-MM-DD] [...row flags]
heliox tool ahrefs -- pages top        --target example.com [...row flags]
heliox tool ahrefs -- competitors      --target example.com --country us [...row flags]   # --country REQUIRED

# Keyword research (Keywords Explorer): no target; --keywords + --country
heliox tool ahrefs -- keyword overview --keywords "seo,backlinks" --country us
heliox tool ahrefs -- keyword ideas    --keywords "seo" --country us --kind matching|related|suggestions
heliox tool ahrefs -- keyword volume-history --keyword "seo" --country us [--from YYYY-MM-DD] [--to YYYY-MM-DD]

# SERP for a keyword (one row per ranking position)
heliox tool ahrefs -- serp --keyword "seo tools" --country us [--top-positions 10] [--date YYYY-MM-DD]

# Compare many targets in one call (unit-efficient)
heliox tool ahrefs -- batch --targets "ahrefs.com,example.com" [--country us] [--select url,domain_rating,backlinks,refdomains,org_traffic,org_keywords]
```

## Shared rows flags

The backlinks / refdomains / keywords / pages / competitors commands accept the
same filter grammar:

- `--select f1,f2,...`: fields to return. Defaults are curated; override only
  when you need different columns (costs units per field).
- `--where '<expr>'`: Ahrefs' documented filter expression, passed through
  **verbatim** (e.g. `domain_rating_source>50`). The tool invents no DSL.
- `--order-by 'field:desc'`, `--limit N` (default 10), `--offset N`.
- `--mode exact|prefix|domain|subdomains`, `--protocol both|http|https`: how
  the `--target` is interpreted (site-explorer commands only).

`--country` is an ISO code (e.g. `us`, `gb`). It is **required** for
`competitors`, `keyword overview/ideas/volume-history`, and `serp`; optional
elsewhere.

## Connect notes

- The user supplies an **Ahrefs API v3 key**, created at Account settings >
  API keys. Only workspace owners and admins can reach that screen, so relay
  that requirement when you ask for one: a member seat cannot produce a key.
- **The key is account-wide, and you should say so when asking for it.** Ahrefs
  offers no scope, permission, or read-only choice at creation: the only inputs
  are a name and a monthly API-unit cap. One key reaches every product the
  workspace subscription includes (Site Explorer, Rank Tracker, Site Audit,
  Management (including its project-write endpoints), GSC Insights, Social
  Media), which is strictly more than the read-only commands above use. Ahrefs'
  own OAuth path is no narrower (a single fixed scope that mints the same
  account-wide key), so there is no tighter alternative to offer.
- The admin's real levers are the **per-key monthly API-unit cap** and deleting
  the key. Suggest a dedicated key for Helio with a cap, rather than reusing one
  that other integrations already spend.
- A key lives **1 year**, then expires. Expiry and revocation both surface as
  **401 reconnect required**; ask the user to create a fresh key and reconnect.
  There is no refresh cycle and no silent renewal.
- Requests are rate-limited (default 60/min); a `429` surfaces verbatim with the
  HTTP status. Re-invoke later rather than tight-looping.
- Add `--json` to render any error as a `{"error":{message,kind,status}}`
  envelope on stderr instead of plain text.
