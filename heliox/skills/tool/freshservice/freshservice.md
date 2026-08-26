# Freshservice (`heliox tool freshservice -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Freshservice is
a **flat provider** (not grouped like `google`): everything after `--` is the
freshservice tool's own CLI.

```bash
heliox tool freshservice [--account <key>] -- <resource> <verb> [flags...]
```

Freshservice is IT Service Management (ITSM). You work a service desk the way a
human agent does: triage incoming tickets (incidents + service requests), reply
to the requester or add a private note, reassign / retag / change
status·priority·group, look up the requester and the agent/group to route to,
filter the queue, and (the ITSM differentiator) look up **CMDB assets**
referenced by a ticket.

## Connecting

The credential is **one URL-shaped string** that carries both the account domain
and the API key:

```
https://<api_key>@<your-domain>.freshservice.com
```

Find the API key in Freshservice under **Profile Settings** (below the
change-password box). The connected key inherits that agent profile's
permissions, so it should belong to an agent with the ticket/asset scope you
need. The account is identified by its domain (`<your-domain>.freshservice.com`).
That is the `--account` key when more than one is connected. A bad key/domain
is not caught at connect time; it surfaces as a `401 reconnect required` on the
first call.

## Command tree

```bash
# Tickets
heliox tool freshservice -- ticket list    [--updated-since T] [--per-page N] [--page N]   # GET /tickets
heliox tool freshservice -- ticket search  --query "status:2 AND priority:1" [--page N]     # GET /tickets/filter
heliox tool freshservice -- ticket get     <id> [--conversations]
heliox tool freshservice -- ticket create  --subject S --description D --email E \
                                           [--status ST] [--priority P] [--group-id G] [--agent-id A] [--type T]
heliox tool freshservice -- ticket update  <id> [--status ST] [--priority P] [--group-id G] [--agent-id A] [--tags a,b]
heliox tool freshservice -- ticket reply   <id> --body BODY        # public reply to the requester
heliox tool freshservice -- ticket note    <id> --body BODY [--private=false]   # private note by default

# People + routing
heliox tool freshservice -- requester list [--email E] [--per-page N] [--page N]
heliox tool freshservice -- requester get  <id>
heliox tool freshservice -- agent list     [--email E] [--per-page N] [--page N]
heliox tool freshservice -- agent get      <id>
heliox tool freshservice -- group list     [--per-page N] [--page N]

# CMDB assets
heliox tool freshservice -- asset list     [--filter "name:'MacBook'"] [--per-page N] [--page N]
heliox tool freshservice -- asset get      <display-id>
```

## Output shape

Every command prints one JSON object to stdout. Standard list commands wrap
results:

```json
{"items": [...], "page": 2, "per_page": 30, "next_page": 3}
```

`next_page` is `null` on the last page (derived from Freshservice's `link`
header; you never parse the raw envelope). **`ticket search` is different**: the
`/tickets/filter` endpoint sends no `link` header, so its output adds a `total`
count and `next_page` is derived from it:

```json
{"items": [...], "page": 1, "per_page": 30, "total": 65, "next_page": 2}
```

Page through search results by following `next_page` (or by walking pages
`1..ceil(total/30)`, capped at 10). Get / create / update / reply / note return
the bare resource object (the `{"ticket": {...}}` envelope is unwrapped for you).
Errors go to stderr as `{"error":{"status":<http>,"message":...,
"provider_code":...}}`, plus `retry_after` on a 429.

## `ticket list` vs `ticket search`: different pagination, on purpose

They are separate commands because the endpoints page differently and a flag
must never silently change meaning:

- **`ticket list`** (`GET /tickets`): `--per-page` adjustable up to **100**;
  `--page` walks the whole dataset.
- **`ticket search`** (`GET /tickets/filter`): the endpoint **fixes 30
  results/page and ignores per_page**, so there is **no `--per-page`**; `--page`
  is **1-10** (hard cap 300 results, out of range is rejected). This endpoint
  returns **no `link` header**: the output carries a `total` count and
  `next_page` is derived from it (see Output shape). Narrow a broad query with a
  `created_at:>'YYYY-MM-DD'` clause to stay under the 300-result cap.

### Filter query syntax (`ticket search --query`)

A Lucene-like expression over ticket fields, combined with `AND`/`OR`:

```
status:2 AND priority:1
group_id:12 AND status:2
agent_id:0                       # unassigned (responder_id is null)
created_at:>'2026-06-01' AND type:'Incident'
```

Send the raw expression; the tool wraps it in the quotes Freshservice requires.

## Enum codes: the create/update APIs take INTEGER codes, not labels

`--status`, `--priority`, and the source field are **integers**. Sending a label
string ("Open", "High") is rejected. `--type` is the exception: a **string**.

**status:** `2` Open · `3` Pending · `4` Resolved · `5` Closed
(accounts may add custom statuses with codes ≥ 6).

**priority:** `1` Low · `2` Medium · `3` High · `4` Urgent.

**source:** `1` Email · `2` Portal · `3` Phone · `4` Chat · `5` Feedback widget ·
`6` Yammer · `7` AWS CloudWatch · `8` PagerDuty · `9` Walkup · `10` Slack ·
`11` Chatbot · `12` Workplace · `13` Employee Onboarding · `14` Alerts ·
`15` MS Teams · `18` Employee Offboarding.

**type:** a **string**, not a code, e.g. `"Incident"` (default) or
`"Service Request"`. Whatever ticket types the account defines are valid.

## `ticket create`: required fields and the defaults the tool applies

`--subject`, `--description`, and `--email` (the requester's email) are required.
Because an API key always creates on behalf of a requester (the agent-side path),
the tool **supplies `--status 2` (Open) and `--priority 2` (Medium) when you omit
them** so the create doesn't fail; both are overridable.

Caveats there is no create-time escape hatch for (`bypass_mandatory` exists only
on update, not create):

- An account **priority matrix** (Admin → Priority Matrix) can override the
  `priority` you send.
- Account-configured **mandatory custom fields** (and sometimes `department_id`)
  can still 400 a create with fields this synopsis doesn't list. The error body
  is surfaced verbatim: read `errors[]` to see exactly which field the account
  requires, then re-send with it.
- To leave a ticket **unassigned**, omit `--agent-id` (a `null` responder is
  rejected).

## Safety

Replying to a requester (`ticket reply`) and creating tickets are outward-facing
actions: follow the sensitive-operation rule in [../SKILL.md](../SKILL.md).
Prefer a private `ticket note` over a public `ticket reply` when you are only
recording internal context. Never echo the credential URL; the CLI never shows
it to you.
