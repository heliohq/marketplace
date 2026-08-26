# Lemlist (`heliox tool lemlist -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Lemlist is a
**flat provider** (not grouped like `google`): everything after `--` is the
lemlist tool's own CLI. Lemlist is a cold-outreach / sales-engagement platform
(multichannel email + LinkedIn sequences).

```bash
heliox tool lemlist [--account <key>] -- <resource> <verb> [flags...]
```

Auth is handled for you (the user's API key is injected per call). Every leaf
takes `--json` and prints Lemlist's JSON on stdout. Exit codes: `0` success,
`1` API/runtime error (a `--json` error envelope carries the HTTP status), `2`
usage error.

## Command surface

Grouped by resource: `team`, `campaign`, `lead`, `activity`, `unsubscribe`.

### team: account context (start here)

```bash
heliox tool lemlist -- team get --json        # account identity (team _id + name)
heliox tool lemlist -- team senders --json    # sending members + their campaigns
heliox tool lemlist -- team credits --json    # remaining enrichment/send credits
```

### campaign: enumerate, inspect, report, control

```bash
heliox tool lemlist -- campaign list --status running --limit 50 --json
heliox tool lemlist -- campaign get <campaignId> --json
heliox tool lemlist -- campaign stats <campaignId> \
  --start-date 2026-01-01 --end-date 2026-01-31 --json           # opens/clicks/replies/bounces (dates required)
heliox tool lemlist -- campaign start <campaignId> --json        # resume the sequence
heliox tool lemlist -- campaign pause <campaignId> --json
```

`campaign list` filters: `--status` (running|draft|archived|ended|paused|errors),
`--sort-by createdAt`, `--sort-order asc|desc`, `--offset`/`--limit`/`--page`.
`campaign stats` **requires** both `--start-date` and `--end-date` (ISO 8601):
Lemlist rejects a windowless call, so omitting either is a usage error (exit 2)
before any request is made.

### lead: enroll, look up, update, dispose

```bash
# enroll a lead into a campaign (email required; extra fields via flags or --fields)
heliox tool lemlist -- lead add <campaignId> --email jane@acme.com \
  --first-name Jane --company-name Acme --json
heliox tool lemlist -- lead add <campaignId> --email jane@acme.com \
  --fields '{"customVar":"vip"}' --json

# look up a lead (need --email OR --id)
heliox tool lemlist -- lead get --email jane@acme.com --json

# update a lead's fields inside a campaign
heliox tool lemlist -- lead update <campaignId> <leadId> --fields '{"firstName":"J"}' --json

# stop contacting: unsubscribe keeps the lead, delete removes it entirely
heliox tool lemlist -- lead unsubscribe <campaignId> <email> --json   # suppress, by EMAIL
heliox tool lemlist -- lead delete <campaignId> <leadId> --json       # force-delete, by lead ID (sends action=remove)

# pipeline disposition after a reply (accepts a lead id or email)
heliox tool lemlist -- lead mark-interested <leadIdOrEmail> --json
heliox tool lemlist -- lead mark-not-interested <leadIdOrEmail> --json
```

### activity: the event stream

```bash
# opens, clicks, replies, bounces (version=v2 is sent for you)
heliox tool lemlist -- activity list --type emailsReplied --campaign-id <id> --json
heliox tool lemlist -- activity list --min-date 2026-01-01T00:00:00Z --limit 100 --offset 0 --json
```

`activity list` is **not** cursor-paginated: to read everything, increment
`--offset` by `--limit` each call (0, 100, 200, …). Filters: `--type`,
`--campaign-id`, `--lead-id`, `--min-date`/`--max-date`, `--is-first`.

### unsubscribe: suppression list (compliance)

```bash
heliox tool lemlist -- unsubscribe list --json
heliox tool lemlist -- unsubscribe add jane@acme.com --json      # email or a whole domain
heliox tool lemlist -- unsubscribe add acme.com --json
heliox tool lemlist -- unsubscribe delete jane@acme.com --json
```

## Footguns

- **`lead get` needs `--email` or `--id`**: with neither it is a usage error
  (exit 2), no call is made.
- **`lead update` / `lead unsubscribe` / `lead delete` are campaign-scoped**:
  they take the `<campaignId>` first. `mark-interested` /
  `mark-not-interested` are account-wide (lead id or email only).
- **`lead unsubscribe` (by email) and `lead delete` (by lead id) are different
  operations.** `unsubscribe` suppresses the lead but keeps it; `delete` sends
  `action=remove` and force-deletes it. Don't pass a lead id to `unsubscribe`
  or an email to `delete`: the id/email argument shape differs per verb.
- **Adding a lead does not start the campaign.** Enroll leads, then
  `campaign start <id>` if it is not already running.
- **`campaign stats` is the reporting endpoint**, not `campaign get`: `get`
  returns configuration, `stats` returns the open/click/reply/bounce numbers.
