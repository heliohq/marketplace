# Hunter (`heliox tool hunter -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Hunter is a
**flat, API-key provider**: the user pastes their Hunter API key once (no OAuth
consent screen), and everything after `--` is Hunter's own CLI speaking the
Hunter v2 API with that key injected automatically.

```bash
heliox tool hunter [--account <key>] -- <command> [flags...]
```

Hunter is a prospecting / email-intelligence utility: find someone's email,
verify an address is deliverable before you send, enrich a contact or company,
build prospect lists, and check your remaining quota. Every command prints the
provider JSON verbatim; run `-- <command> --help` for the full flag surface.

## Find an email

```bash
heliox tool hunter -- email-finder --domain stripe.com --first-name Jane --last-name Doe
heliox tool hunter -- email-finder --linkedin-handle janedoe        # by LinkedIn instead of name+domain
heliox tool hunter -- domain-search --domain stripe.com --limit 10  # everyone Hunter knows at a domain
heliox tool hunter -- email-count --domain stripe.com               # free: how many emails exist for a domain
```

`domain-search` and `email-finder` spend one search credit per call;
`email-count`, `domain-finder`, `account`, and all lead commands are free.

## Verify before you send (the 202 protocol)

```bash
heliox tool hunter -- email-verifier --email jane@stripe.com
```

Verification can take ~20 seconds. If Hunter is still working it returns a
body whose `data.status` is `accepted`/pending rather than a final result.
**Re-run the exact same command to poll** (each poll costs one request). There
is no client-side wait loop by design: you decide when to re-check. Read
`data.result` (`deliverable` / `undeliverable` / `risky`) and `data.status`
before trusting an address.

## Enrich a contact or company

```bash
heliox tool hunter -- enrich person --email jane@stripe.com     # or --linkedin-handle
heliox tool hunter -- enrich company --domain stripe.com
heliox tool hunter -- enrich combined --email jane@stripe.com   # person + company in one call
heliox tool hunter -- domain-finder --company "Stripe"          # company name -> domain (free, beta)
```

Enrichment returns `404` when Hunter has no record for that person/company.
That is a normal "not found", not an auth failure.

## Discover companies and build lead lists

```bash
heliox tool hunter -- discover --query "SaaS companies in France"
heliox tool hunter -- discover --filters '{"headcount":"50-100","industry":["saas"]}'
```

`discover` takes a natural-language `--query`, a raw-JSON `--filters` object
(merged into the request body: pass any structured filter Hunter's docs list;
your account's plan gates which premium filters resolve), or both.

Save and manage prospects with the `lead` and `lead-list` CRUD verbs:

```bash
heliox tool hunter -- lead-list create --name "Q3 Prospects"
heliox tool hunter -- lead create --email jane@stripe.com --first-name Jane --company Stripe --leads-list-id 42
heliox tool hunter -- lead list --leads-list-id 42
heliox tool hunter -- lead update --id 9 --position CTO
heliox tool hunter -- lead delete --id 9
```

`lead create`/`update` take explicit flags for the common fields plus
`--attributes '{...}'` raw JSON for anything else (including custom
attributes); explicit flags win over overlapping `--attributes` keys.

## Check your quota

```bash
heliox tool hunter -- account
```

Free. Returns the plan, searches-used-vs-available, verifications-used-vs-
available, and the monthly `reset_date`. Check this first when a run needs
many paid calls. Free plans are small (e.g. 25 searches/month).

## Footguns

- **403 = rate limited, 429 = quota exhausted**, inverted from most APIs.
  Neither is a bad key: a 403 means slow down and retry shortly; a 429 means
  the monthly quota is spent (nothing to do until `reset_date` or an upgrade).
  Only a `401` means the key itself is invalid; reconnect then.
- **Prefer the free commands** (`account`, `email-count`, `domain-finder`,
  `lead*`) for exploratory work; spend `domain-search` / `email-finder` /
  `email-verifier` credits deliberately, once each where you can.
- **Quota is per account, not per key**: two keys from the same Hunter account
  share one pool and resolve to the same connection.
- **The key rides the `X-API-KEY` header**, never a URL query param, so it
  never appears in logs.

## Safety

Hunter reads and stores third-party personal contact data (emails, names,
company affiliations). Treat found addresses and enriched profiles as
sensitive: use them only for the task the user sanctioned, and follow the
sensitive-operation rule in `../SKILL.md` before acting on the data
(e.g. adding people to an outreach list or contacting them).
