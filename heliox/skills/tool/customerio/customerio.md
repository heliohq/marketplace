# Customer.io (`heliox tool customerio -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Customer.io is
a **flat provider** (not grouped like `google`): everything after `--` is the
customerio tool's own CLI. It wraps the Customer.io **App API**: the
read-and-manage surface a messaging-automation teammate uses.

```bash
heliox tool customerio [--account <key>] -- <resource> <verb> [flags...]
```

## Connect (API key, not OAuth)

Customer.io has no OAuth for its Journeys APIs, so you connect with an **App API
key**:

1. `heliox tool customerio auth --json` mints the connect link. Send it to the
   user and explain what you need it for.
2. The user creates the key in **Account Settings → API Credentials** (or
   **Workspace Settings → API and webhook credentials**),
   https://fly.customer.io/settings/api_credentials?keyType=app. The key is
   **scoped to one workspace** and its **permissions are fixed at creation**:
   an under-scoped key must be re-created. Ask for read access to people,
   campaigns, segments, newsletters, broadcasts, messages, and exports, plus
   send permission for transactional email and broadcast triggering.
3. The key is verified against `GET /v1/workspaces` and stored; you never see
   it. `heliox tool list --json` then shows the connection.

**Region:** the tool defaults to the US region. For an EU-region account, pass
`--region eu` after `--` (e.g. `-- --region eu workspace list`). Note the
connect-time verification is US-only today, so EU accounts are a known
limitation for the connect step.

**The Track API is not wrapped** (identify/track events, attribute writes). This
tool is the App API only: reporting, people lookup, segments, transactional
send, broadcasts, and exports.

## Core flows

### "Did Jane get the onboarding email? Why not?"

```bash
# find the person by email
heliox tool customerio -- person search --email jane@example.com
# their delivery history (the "did she get it" answer)
heliox tool customerio -- person messages --id <customer_id>
# their profile + segments + activity log
heliox tool customerio -- person get --id <customer_id>
heliox tool customerio -- person segments --id <customer_id>
heliox tool customerio -- person activities --id <customer_id>
```

`--id` defaults to a Customer.io customer id; pass `--id-type email` or
`--id-type cio_id` to resolve `--id` differently.

### Campaign / newsletter / broadcast reporting

```bash
heliox tool customerio -- campaign list
heliox tool customerio -- campaign metrics --id <id> --period days --steps 14
heliox tool customerio -- campaign metrics --id <id> --links      # per-link clicks
heliox tool customerio -- campaign metrics --id <id> --journey    # journey metrics
heliox tool customerio -- newsletter metrics --id <id>
heliox tool customerio -- broadcast metrics --id <id>
heliox tool customerio -- transactional metrics --id <id>
heliox tool customerio -- message list --metric bounced --type email   # workspace-wide delivery search
```

### Segments (manual-segment lifecycle)

```bash
heliox tool customerio -- segment list
heliox tool customerio -- segment create --name "VIPs" --description "top accounts"
heliox tool customerio -- segment get --id <id> --count      # member count
heliox tool customerio -- segment members --id <id>
heliox tool customerio -- segment delete --id <id>
```

### Send a transactional email

```bash
heliox tool customerio -- send email \
  --transactional-id <id> --to jane@example.com \
  --identifier email=jane@example.com \
  --message-data '{"first_name":"Jane"}'
```

`--identifier` is repeatable `key=value` (`email=`, `id=`, `cio_id=`).

### Trigger an API broadcast

```bash
heliox tool customerio -- broadcast trigger --id <broadcast_id> \
  --data '{"promo":"summer"}' --emails jane@example.com,joe@example.com
heliox tool customerio -- broadcast status --id <broadcast_id> --trigger <trigger_id> --errors
```

Audience is at most one of `--emails`, `--ids`, `--per-user-data`, or
`--data-file-url`; omit all to use the broadcast's own configured audience.
**Rate limit: one trigger request per 10 seconds per broadcast** (the general
App API limit is 10 req/s). Do not retry a trigger in a tight loop.

### Bulk exports (for analysis)

```bash
heliox tool customerio -- export deliveries --campaign <id> --start <unix> --end <unix>
heliox tool customerio -- export people --filters '<json>'   # audience filter is required
heliox tool customerio -- export list
# poll the export until its status is ready, then save the file:
heliox tool customerio -- export get --id <export_id>
heliox tool customerio -- export get --id <export_id> --download --out ./deliveries.csv
```

`export get --id <id>` returns the export's metadata (including its `status`);
poll it until the export is finished. `export get --download` then fetches a
signed link from `GET /v1/exports/{id}/download` (the export object itself has no
link, only a `downloads` counter), follows it, and writes the file, emitting
`{"ok":true,"path":...,"bytes":N}`. The signed link expires 15 minutes after it
is issued. If it errors with "no download url yet", the export is still
processing. Poll `export get --id <id>` first.

## Notes

- Every JSON-returning command prints the provider's JSON verbatim: the shapes
  are Customer.io's documented App API responses.
- `workspace list` doubles as a connectivity check.
- For any command, `--help` after `--` is the full flag reference.
