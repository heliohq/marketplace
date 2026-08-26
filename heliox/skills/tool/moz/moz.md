# Moz (`heliox tool moz -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Moz is a
**flat provider** (not grouped like `google`): everything after `--` is the
moz tool's own CLI.

```bash
heliox tool moz [--account <key>] -- <group> <verb> [flags...]
```

Moz is **SEO authority + link + keyword data** over the Moz API: Domain/Page
Authority and spam score, Brand Authority, backlinks and linking root domains,
anchor-text profiles, keyword volume/difficulty/CTR/intent, and the keywords a
site ranks for. Connect with a **Moz API token** (generated in the Moz API
dashboard, `moz.com/api/dashboard`). The Moz API is a separate subscription
from Moz Pro; a free tier of 50 rows/month exists.

## Quota: read this before large pulls

**Every returned row debits the account's monthly row quota**, metered from one
shared balance. `quota` and `index` are free; single-object fetches
(`site metrics`, `keyword metrics`, `keyword intent`, `ranking-keywords count`)
cost ~1 row; **list** commands cost one row per returned row. To protect the
balance:

- Every list command defaults to `--limit 25`. Only raise it when you
  deliberately need more rows.
- Check the balance first (it is free):

  ```bash
  heliox tool moz -- quota
  ```

## Output shape

The tool passes Moz's JSON `result` through verbatim (one JSON object per call,
newline-terminated). Errors go to stderr and set a non-zero exit code:
a JSON-RPC error (e.g. a URL not in Moz's index) exits 1; a bad flag exits 2.

## Core commands

```bash
# Authority + spam for one URL (repeat --site for a single batched call)
heliox tool moz -- site metrics --site moz.com
heliox tool moz -- site metrics --site moz.com --site ahrefs.com --scope root_domain

# Brand Authority (domain-level)
heliox tool moz -- site brand-authority --site moz.com

# Top pages by authority
heliox tool moz -- site top-pages --site moz.com --limit 25

# Backlinks, linking root domains, anchor text (target_query-scoped)
heliox tool moz -- link list --site moz.com --limit 25
heliox tool moz -- link domains --site moz.com
heliox tool moz -- link anchors --site moz.com

# Keyword research
heliox tool moz -- keyword metrics --keyword "seo tools" --locale en-US
heliox tool moz -- keyword suggestions --keyword "seo tools" --limit 25
heliox tool moz -- keyword intent --keyword "seo tools"

# Keywords a site ranks top-50 for (list + free count)
heliox tool moz -- ranking-keywords list --site moz.com --limit 25
heliox tool moz -- ranking-keywords count --site moz.com

# Index freshness (free)
heliox tool moz -- index
```

`--scope` takes Moz's real scope values: `page`, `subdomain`, or `root_domain`
(omit it to use the API default). Note this is not `domain` or `url`.

## Escape hatch: any method

The Moz API exposes many more methods than the typed commands above. Reach any
of them with the raw JSON-RPC `call`, the method name plus a `--data` object
that becomes `params.data`:

```bash
heliox tool moz -- call --method data.site.link.status.fetch \
  --data '{"target_query":{"query":"moz.com","scope":"root_domain"}}'
```

Use `call` when you need a method (link status/filter variants, metric
histories/distributions, redirect lookups, Moz Local, …) that has no typed
subcommand yet.
