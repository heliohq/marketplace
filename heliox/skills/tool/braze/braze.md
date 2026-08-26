# Braze (`heliox tool braze -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Braze is a
**flat provider** (not grouped): everything after `--` is the braze tool's own
CLI.

```bash
heliox tool braze [--account <key>] -- <resource> <verb> [flags...]
```

Braze is a **customer-engagement platform** (push, email, SMS, in-app). This
tool covers two intents: **read** (campaign / Canvas / segment / KPI analytics
and content discovery) and **act** (trigger/schedule messages and look
up/track users). Everything returns Braze's JSON on stdout verbatim.

## Connect model (read this: it is not OAuth)

Braze has **no multi-tenant OAuth**. The user connects by pasting a single
**connection string** that carries both the REST API key and the workspace's
cluster host:

```
https://<REST_API_KEY>@<cluster-rest-host>
# example: https://a1b2c3d4-....@rest.iad-05.braze.com
```

Two things the user must supply, both from the Braze dashboard:

- **REST API key**: created under **Settings → APIs and Identifiers → Create
  API Key**. At creation the user assigns **endpoint permissions** (e.g.
  `campaigns.data_series`, `messages.send`, `users.track`). Permissions are
  **immutable** after creation. A broader scope means a new key.
- **Cluster REST host**: Braze is regional and multi-instance; every workspace
  lives on exactly one cluster (`rest.iad-05.braze.com`, `rest.fra-01.braze.eu`,
  …). It is listed in **Settings → APIs and Identifiers** and in the instance
  table at `braze.com/docs/api/basics`. There is **no default**: the wrong host
  is a total failure, so it is captured at connect and stored with the key.

The `account` key for a connected workspace is its cluster REST host.

## The permission model IS the guardrail

The stored key carries exactly the endpoint permissions its creator granted, so
the key (not the tool) gates what you can do. React to the two failures
differently:

- **`403` (permission)**: the key is valid but **lacks the endpoint
  permission** for this call (e.g. a read-only key hitting `messages send`). The
  key is alive for its own scope. Tell the user to **reconnect with a
  broader-scoped REST API key** (permissions can't be edited; they create a new
  key). Do **not** treat this as a dead key.
- **`401` (credential)**: the key is invalid or revoked. Ask the user to
  disconnect + reconnect with a valid key.

## Read / export / discovery (all safe, GET unless noted)

```bash
# Campaigns
heliox tool braze -- campaigns list --json
heliox tool braze -- campaigns details --campaign-id <id> --json
heliox tool braze -- campaigns series --campaign-id <id> --length 14 --ending-at 2026-07-01 --json
heliox tool braze -- sends series --campaign-id <id> --send-id <sid> --length 7 --json

# Canvas (multi-step journeys)
heliox tool braze -- canvas list --json
heliox tool braze -- canvas details --canvas-id <id> --json
heliox tool braze -- canvas series  --canvas-id <id> --length 14 --ending-at 2026-07-01 --json
heliox tool braze -- canvas summary --canvas-id <id> --length 14 --ending-at 2026-07-01 --json

# Segments
heliox tool braze -- segments list --json
heliox tool braze -- segments details --segment-id <id> --json
heliox tool braze -- segments series  --segment-id <id> --length 14 --json

# Workspace KPIs
heliox tool braze -- kpi dau        --length 14 --json
heliox tool braze -- kpi mau        --length 30 --json
heliox tool braze -- kpi new-users  --length 14 --json
heliox tool braze -- kpi uninstalls --length 14 --json

# Events / purchases / sessions
heliox tool braze -- events list --json
heliox tool braze -- events series --event purchase --unit day --length 30 --json
heliox tool braze -- purchases series --metric revenue --length 30 --json
heliox tool braze -- sessions series --length 14 --json

# Content discovery (read-only)
heliox tool braze -- templates email list --json
heliox tool braze -- templates email info --template-id <id> --json
heliox tool braze -- content-blocks list --json
heliox tool braze -- content-blocks info --content-block-id <id> --json

# User-profile lookup (POST /users/export/ids under the hood)
heliox tool braze -- users export --external-id <id> --fields email --fields custom_attributes --json
```

## Act: messaging + user data (permission-gated, acts on LIVE customer data)

These send real messages or mutate real user profiles. Treat every one as an
outward-facing sensitive operation (see `../SKILL.md`): confirm intent
with the user first. Complex Braze bodies (the `messages` object, trigger
properties, attribute/event arrays) are passed through as **raw JSON**. Do not
try to have the tool re-model them.

```bash
# Immediate + scheduled sends
heliox tool braze -- messages send --body '{"broadcast":true,"messages":{...}}' --json
heliox tool braze -- messages schedule --body '{"messages":{...}}' --schedule '{"time":"2026-07-04T17:00:00Z"}' --json
heliox tool braze -- messages scheduled-list --end-time 2026-08-01T00:00:00Z --json

# API-triggered campaigns / Canvases (id set by the tool; recipients in --body)
heliox tool braze -- campaigns trigger --campaign-id <id> --body '{"recipients":[...]}' --json
heliox tool braze -- canvas trigger    --canvas-id <id>  --body '{"recipients":[...]}' --json

# Subscription-group state
heliox tool braze -- subscription status-get --external-id <id> --json
heliox tool braze -- subscription status-set --subscription-group-id <gid> --state unsubscribed --email a@b.co --json

# Identify / track (attributes, events, purchases as raw JSON arrays)
heliox tool braze -- users track --attributes '[{"external_id":"u1","first_name":"A"}]' --json
```

## Rate limits

Braze's default is a high **250,000 requests/hour**, but several endpoints are
much tighter (e.g. `users/track` and the `messages/send` /
`campaigns/trigger/send` / `canvas/trigger/send` families: broadcast sends can
be as low as ~250/min). A **`429` (rateLimit)** error is transient: Braze does
not send `Retry-After`, so the error carries `rate_limit_reset` (the
**UTC epoch-seconds** time the window resets). Wait until then and retry; do not
treat it as a permanent failure.

## Out of scope (v1)

Destructive/identity ops (`users/delete`, alias/merge), catalog/Media/Preference
Center writes, bulk imports, and template/Content-Block **creation** are not
exposed: read-only for content, no destructive user ops. If the user needs
one, say so rather than improvising another path.
