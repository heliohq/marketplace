# Snov.io (`heliox tool snov`)

Snov.io is a sales-intelligence platform: find a prospect's business email,
verify it is deliverable, and enrich a person from an email. Use it when a task
needs to reach or research a specific person or company by email.

Read `../SKILL.md` first for the connect/use model. Snov is a **flat** provider
(`heliox tool snov -- …`).

## Connect

Snov uses the user's own API credentials, not an OAuth consent screen. When
`heliox tool list` shows no snov row, ask the user to connect:

```bash
heliox tool snov auth --json
```

Relay the link. In the connect drawer the user pastes two values from
**Snov.io → Settings → API**: their **API user ID** (client_id) and **API
secret key**. API access requires a **paid Snov plan**: the free trial
excludes the API. You are woken when the connection lands; do not poll.

## Commands

Everything after `--` goes to the tool. Every command emits JSON.

```bash
# Account credits: also the connectivity / credential check (free).
heliox tool snov -- account balance

# How many emails Snov has for a domain (free pre-check).
heliox tool snov -- email count --domain example.com

# Find all business emails for a company domain (consumes credits).
heliox tool snov -- email find domain --domain example.com

# Find one person's email from their name + company domain (consumes credits).
heliox tool snov -- email find by-name --first Jane --last Doe --domain example.com

# Verify deliverability before sending (consumes credits; repeat --email up to 10).
heliox tool snov -- email verify --email jane@example.com

# Enrich a person profile from a known email (consumes credits).
heliox tool snov -- enrich by-email --email jane@example.com
```

The finder and verifier are asynchronous on Snov's side; the tool waits for the
task to finish and returns only the completed result: you never handle a raw
task hash. If a task is slow, raise the wait with `--timeout` (e.g.
`--timeout 90s`).

## Cost & safety

- `email find …`, `email verify`, and `enrich by-email` **consume Snov
  credits**. `account balance` and `email count` are free. Prefer `email count`
  as a cheap pre-check before a domain search, and check `account balance` if
  you are unsure the user has credits left.
- A `401` / credential-rejected error means the stored API user ID / secret is
  wrong or the plan lapsed: ask the user to reconnect via a fresh `auth` link.
- Contact data is personal information: use found emails only for the task the
  user asked for; do not bulk-scrape or repurpose them.
