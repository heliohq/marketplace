# Instantly (`heliox tool instantly -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Instantly is a
**flat provider** (not grouped like `google`): everything after `--` is the
instantly tool's own CLI.

```bash
heliox tool instantly [--account <key>] -- <group> <verb> [flags...]
```

Instantly is a cold-email outreach platform (API v2): campaigns, sending
accounts + warmup, lead management, the unified inbox ("Unibox"), email
verification, and deliverability analytics. Output is raw provider JSON
passthrough (snake_case), so it matches the official docs 1:1.

## Connect

Instantly uses an **API key**, not OAuth. The user creates a workspace-scoped
key in the dashboard (Settings → Integrations → API Keys,
https://app.instantly.ai/app/settings/integrations) and pastes it into the
connect drawer. The key is shown **once** and is scoped at creation:

- The connection is verified against `GET /workspaces/current`, so the key
  **must carry `workspaces:read`** (or a wildcard like `all:read` / `all:all`)
  or the connect step fails.
- For real work, the key also needs the scopes for what you do:
  `campaigns:read`, `leads:all`, `emails:all`, `accounts:read`, etc. Ask the
  user to grant `all:read`+`all:write` (or `all:all`) unless they want to
  restrict you. Tell them which scopes when you send the connect link.
- **API v2 requires a paid plan** (commonly Hypergrowth or higher). A `402`
  ("Workspace does not have an active paid plan") means the key is valid but
  the plan does not include API access. Relay that to the user; do not retry.

## Command groups

Run `-- <group> --help` or `-- <group> <verb> --help` for exact flags rather
than guessing. List commands accept `--limit` and `--starting-after` (pass the
prior response's `next_starting_after` back to page).

### campaign: the core object (reporting + start/stop are the top asks)

```bash
heliox tool instantly -- campaign list --status <code> --limit 50 --json
heliox tool instantly -- campaign get --id <id> --json
heliox tool instantly -- campaign activate --id <id>          # start sending
heliox tool instantly -- campaign pause    --id <id>          # stop sending
heliox tool instantly -- campaign sending-status --id <id> --json
heliox tool instantly -- campaign analytics --id <id> --start-date 2026-01-01 --end-date 2026-01-31 --json
heliox tool instantly -- campaign analytics-overview --ids <id1,id2> --json
heliox tool instantly -- campaign analytics-daily --campaign-id <id> --json
heliox tool instantly -- campaign analytics-steps --campaign-id <id> --json
# create / update take a raw JSON body (sequences + schedule are complex):
heliox tool instantly -- campaign create --data '{"name":"Q1 outbound", ...}' --json
heliox tool instantly -- campaign update --id <id> --data '{"name":"Renamed"}' --json
```

### lead: pipeline upkeep after replies

```bash
# list/search is a POST (complex filter body); pagination rides the body
heliox tool instantly -- lead list --campaign <id> --search "acme" --limit 100 --json
heliox tool instantly -- lead list --data '{"filter":{...}}' --json     # full filter control
heliox tool instantly -- lead get --id <lead-id> --json
heliox tool instantly -- lead create --email a@b.com --campaign <id> --first-name Ada --json
heliox tool instantly -- lead update --id <lead-id> --data '{"company_name":"Acme"}' --json
heliox tool instantly -- lead delete --id <lead-id>
# bulk add (≤1000): the leads array MUST come via --data
heliox tool instantly -- lead add --campaign-id <id> --data '{"leads":[{"email":"a@b.com"}]}' --json
# move is a BACKGROUND JOB (poll with `job get`)
heliox tool instantly -- lead move --to-campaign-id <id> --data '{"ids":["l1","l2"]}' --json
# set interest after a reply (e.g. interested = 1, not interested = -1)
heliox tool instantly -- lead update-interest --lead-email a@b.com --interest-value 1 --json
```

### lead-list: staging leads before campaign assignment

```bash
heliox tool instantly -- lead-list list --json
heliox tool instantly -- lead-list get --id <id> --json
heliox tool instantly -- lead-list create --name "Prospects" --json
heliox tool instantly -- lead-list verification-stats --id <id> --json
```

### email: Unibox triage + reply (the human-inbox half of the loop)

```bash
heliox tool instantly -- email list --is-unread true --campaign-id <id> --json   # 20 req/min cap
heliox tool instantly -- email get --id <email-id> --json
heliox tool instantly -- email unread-count --json
heliox tool instantly -- email reply --eaccount you@you.com --reply-to-uuid <email-id> \
    --subject "Re: hi" --body "Thanks!" --json
heliox tool instantly -- email mark-read --thread-id <thread-id>
```

### account: sender health / warmup / deliverability

```bash
heliox tool instantly -- account list --status <code> --json
heliox tool instantly -- account get --email sender@you.com --json
heliox tool instantly -- account pause  --email sender@you.com
heliox tool instantly -- account resume --email sender@you.com
heliox tool instantly -- account warmup-analytics --emails "a@you.com,b@you.com" --json
heliox tool instantly -- account analytics-daily --start-date 2026-01-01 --json
```

### verify: hygiene before adding leads (async: submit → poll)

```bash
heliox tool instantly -- verify create --email lead@corp.com --json     # may return status "pending"
heliox tool instantly -- verify get --email lead@corp.com --json        # poll until not pending
```

### job: poll bulk-operation completion

```bash
heliox tool instantly -- job list --status running --json
heliox tool instantly -- job get --id <job-id> --json
```

### api: raw escape hatch for the long tail

Subsequences, custom tags, block lists, webhooks, inbox placement. Anything
without a first-class command:

```bash
heliox tool instantly -- api GET subsequences --query limit=10 --json
heliox tool instantly -- api POST custom-tags --data '{"label":"vip"}' --json
```

The path may be bare (`subsequences`), `/api/v2`-prefixed, or a full URL; the
Authorization header is injected and cannot be overridden.

## Footguns (where agents go wrong)

- **`lead list` is a POST, not a GET.** Its filter body is complex; pagination
  (`--limit` / `--starting-after`) rides the body, not the query. Use `--data`
  for anything beyond `--campaign` / `--list-id` / `--search`.
- **Verification is asynchronous.** `verify create` can return
  `status: "pending"`; poll `verify get --email ...` until it resolves. Don't
  treat a pending result as a verdict.
- **Bulk lead moves are background jobs.** `lead move` returns a job; confirm it
  finished with `job get --id <job-id>` before assuming leads landed.
- **`email list` is rate-limited to 20 req/min** (tighter than the workspace
  budget of 100 req/s · 6,000 req/min). Don't poll it in a tight loop.
- **`402` = plan gate, not a bad key.** API v2 needs a paid plan; a `402` means
  relay to the user, not retry. A `401` means the key was revoked; ask them to
  reconnect. A `429` means you hit the rate limit; back off.
- **`--account` when more than one Instantly workspace is connected.** A `409`
  lists candidate account keys; re-run with `--account <key>` before the `--`.
- **This tool does not spend money or manage the workspace.** No DFY
  domain/account purchases, no workspace member/owner changes, no API-key
  rotation, no SuperSearch enrichment (paid credits). Those stay in the human's
  hands; reach them via `api` only if the user explicitly directs it.

## Safety

- **Replies leave the user's account.** `email reply` sends a real email to a
  real prospect, an outward-facing action. Follow the sensitive-operation rule
  in [../SKILL.md](../SKILL.md): draft the reply and confirm with the user
  before sending unless they've pre-authorized the thread.
- **Activating a campaign starts live outreach** to real recipients.
  `campaign activate` and `lead add` into an active campaign begin sending;
  confirm scope before starting or bulk-loading.
- Never echo the API key; the CLI never shows it to you by design.
