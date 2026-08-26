# MailerLite (`heliox tool mailerlite -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. MailerLite is a
**flat provider** (not grouped like `google`): everything after `--` is the
mailerlite tool's own CLI, run against the MailerLite **Connect API**
(`https://connect.mailerlite.com/api`). Auth is a single account API token,
injected for you. You never see or paste it.

```bash
heliox tool mailerlite [--account <key>] -- <resource> <verb> [flags...]
```

Connect is an **API-token** tool: the user generates a token in MailerLite
(Integrations → MailerLite API → Generate new token) and pastes it into the
connect drawer. There is no OAuth consent screen. Regenerating the token in
MailerLite creates a *new* connection row. Use the newest connected account.

Output is the provider's JSON verbatim: lists come back as a `{data, meta,
links}` envelope (cursor- or page-paged), single resources as `{data}`. `--json`
is accepted on every command for uniformity. Errors print a structured
`{"error":{...}}` envelope to stderr; a bad token exits non-zero.

## Command surface

```
subscriber list|get|create|update|delete|count|activity|forget
group      list|create|update|delete|subscribers|assign|unassign
segment    list|subscribers
field      list|create|update|delete
campaign   list|get|create|update|schedule|cancel|delete|report
form       list|get|update|delete|subscribers
automation list|get|activity
webhook    list|create|update|delete
```

### Subscribers (the CRM-of-email core)

```bash
# list / filter (cursor-paged: --limit, --cursor); statuses:
#   active | unsubscribed | unconfirmed | bounced | junk
heliox tool mailerlite -- subscriber list --status active --limit 50 --json
heliox tool mailerlite -- subscriber count --json                 # {"total": N}

# look one up by id OR email
heliox tool mailerlite -- subscriber get jane@example.com --json

# create / upsert (201 new, 200 existing); --fields is a JSON object,
# --groups is a comma list of group ids to add to
heliox tool mailerlite -- subscriber create --email jane@example.com \
  --fields '{"name":"Jane","company":"Acme"}' --groups g1,g2 --json

heliox tool mailerlite -- subscriber update <id> --status unsubscribed --json
heliox tool mailerlite -- subscriber delete <id> --json
heliox tool mailerlite -- subscriber activity <id> --log-name email_open --json
heliox tool mailerlite -- subscriber forget <id> --json           # GDPR erase
```

### Groups & segments (targeting)

```bash
heliox tool mailerlite -- group list --json
heliox tool mailerlite -- group create --name "VIPs" --json
heliox tool mailerlite -- group subscribers <group-id> --status active --json

# assign / unassign a subscriber to a group (the everyday tagging action)
heliox tool mailerlite -- group assign <subscriber-id> <group-id> --json
heliox tool mailerlite -- group unassign <subscriber-id> <group-id> --json

# segments are rule-defined and READ-ONLY over the API
heliox tool mailerlite -- segment list --json
heliox tool mailerlite -- segment subscribers <segment-id> --json
```

### Fields (discover before you write)

Custom fields must exist before `subscriber create/update --fields` can set
them. `field create --type` is one of `text | number | date`.

```bash
heliox tool mailerlite -- field list --json
heliox tool mailerlite -- field create --name "Company" --type text --json
```

### Campaigns (draft → schedule → report)

`list` filters: `--status sent|draft|ready`, `--type regular|ab|resend|rss`
(page-paged: `--limit`, `--page`). Create/update/schedule take a raw JSON body
via `--data` (their payloads nest email blocks and delivery config).

```bash
heliox tool mailerlite -- campaign list --status draft --json
heliox tool mailerlite -- campaign create --data '<campaign JSON>' --json
heliox tool mailerlite -- campaign schedule <id> --data '{"delivery":"instant"}' --json
heliox tool mailerlite -- campaign cancel <id> --json
heliox tool mailerlite -- campaign report <id> --json     # subscriber-activity report
```

### Forms, automations, webhooks

```bash
# forms: list by type (popup|embedded|promotion), then inspect / rename
heliox tool mailerlite -- form list popup --json
heliox tool mailerlite -- form subscribers <form-id> --json

# automations are read-only (no create API)
heliox tool mailerlite -- automation list --json
heliox tool mailerlite -- automation activity <automation-id> --json

# webhooks: --events is a comma list of event names
heliox tool mailerlite -- webhook create --url https://example.com/hook \
  --events subscriber.created,subscriber.updated --json
```

## Footguns

- **Not MailerLite Classic.** This wraps the current **Connect** API only
  (accounts created after 2022-03). Classic accounts use a different API and
  are out of scope.
- **`subscriber update --groups` is destructive on membership**: passing
  `--groups` on update removes the subscriber from any group not listed. To only
  *add* a group, prefer `group assign`.
- **Segments and automations are read-only**: there is no create/schedule API
  for them; you can only list and read their members/activity.
- **`subscriber forget` is a permanent GDPR erase**, not a soft delete. Use
  `subscriber delete` for ordinary removal.
