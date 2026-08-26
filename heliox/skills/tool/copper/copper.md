# Copper CRM (`heliox tool copper -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Copper is a
**flat provider** (not grouped): everything after `--` is the copper tool's own
CLI.

```bash
heliox tool copper [--account <key>] -- <resource> <verb> [flags...]
```

Copper is a sales CRM. The tool wraps the Copper Developer API v1 over the
connected user's OAuth token; every command prints Copper's native JSON on
stdout.

## The mental model (read this first)

- **Records** are the CRM objects: `person` (contacts), `company`, `lead`,
  `opportunity` (deals), `task` (follow-ups). Each has the same verb set:
  `list` / `get` / `create` / `update` / `delete`. `person` also has
  `find-email`.
- **Listing is a search POST, not a GET.** `list` sends `POST
  /{resource}/search` with a JSON filter body: there is no "get all" GET. Use
  the typed filter flags for the common cases and `--json-body` for anything
  else.
- **`activity`** logs notes / calls / emails: `list` / `get` / `create` /
  `delete` (no `update`: activities are immutable once logged).
- **`lookup`** returns the id→name tables you need to build valid create/update
  payloads: `pipelines`, `pipeline-stages`, `customer-sources`, `loss-reasons`,
  `activity-types`, `contact-types`.
- **`account` / `user`** are read-only identity: `account get` (the Copper
  org), `user me` (you), `user list`, `user get --id N` (assignee resolution).

## Core commands

### Read / search

```bash
# whoami
heliox tool copper -- account get --json
heliox tool copper -- user me --json

# search a record type (POST /people/search etc.)
heliox tool copper -- person list --name "Jane" --page-size 20 --json
heliox tool copper -- opportunity list --assignee-id 159258 --json
heliox tool copper -- person find-email --email jane@example.com --json

# fetch one by id
heliox tool copper -- company get --id 123 --json
```

Typed `list` filters: `--name`, `--email`, `--assignee-id`, `--page`,
`--page-size`. For any filter these don't cover (custom fields, tags, date
ranges, sort), pass a raw Copper search body with `--json-body`; it is merged
over the typed flags:

```bash
heliox tool copper -- lead list --json-body '{"tags":["inbound"],"sort_by":"name"}' --json
```

### Write

`create` / `update` take the record payload as `--json-body` (Copper's field
schema is large and per-resource, so there are no typed create flags). Resolve
any referenced ids via `lookup` first.

```bash
heliox tool copper -- person create --json-body '{"name":"Jane Doe","emails":[{"email":"jane@example.com","category":"work"}]}' --json
heliox tool copper -- opportunity update --id 456 --json-body '{"pipeline_stage_id":12,"status":"Won"}' --json
heliox tool copper -- task delete --id 789 --json

# log an activity (type comes from `lookup activity-types`)
heliox tool copper -- activity create --json-body '{"parent":{"type":"person","id":123},"type":{"category":"user","id":0},"details":"Left a voicemail"}' --json
```

### Lookups

```bash
heliox tool copper -- lookup pipelines --json
heliox tool copper -- lookup pipeline-stages --json
heliox tool copper -- lookup activity-types --json
```

## Footguns

- **`list` is `POST /search`, not a plain list.** If you expect a GET-all and
  get nothing, you likely need a filter in the search body: Copper returns a
  page of results, paginated by `--page` / `--page-size`.
- **create/update need `--json-body`.** There are no typed field flags; build
  the payload as JSON, resolving `pipeline_id` / `pipeline_stage_id` /
  `customer_source_id` / activity `type` ids via `lookup`.
- **Rate limit is 600 requests/minute per token.** A 429 surfaces as a runtime
  error (exit 1): back off, don't hammer.
- **`--json`** switches the error channel to a structured envelope; command
  output is always Copper's raw JSON regardless.

## Exit codes

`0` success · `1` Copper API/transport failure (a 401 also means reconnect) ·
`2` usage error (bad flags, invalid `--json-body`, unknown subcommand).
