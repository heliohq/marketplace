# Close (`heliox tool close -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Close is a
**flat provider** (not grouped like `google`): everything after `--` is the
close tool's own CLI over the Close CRM REST API.

```bash
heliox tool close [--account <key>] -- <resource> <verb> [flags...]
```

Close is a sales CRM. The objects you work with: **leads** (companies/accounts,
the central object), **contacts** (people on a lead), **opportunities** (deals
in a pipeline), **activities** (notes/calls/emails logged on a lead), and
**tasks** (follow-up reminders). `search` runs Close's Advanced Filtering query;
`me` shows the connected user and their organizations.

Output is the Close JSON verbatim. List endpoints return
`{"data":[...],"has_more":<bool>}`. Page with `--limit`/`--skip`.

## Core commands

### Read

```bash
heliox tool close -- me --json                                  # who am I + orgs
heliox tool close -- lead list --limit 25 --skip 0 --json       # page through leads
heliox tool close -- lead get <lead-id> --json                  # one lead (with its contacts + opps)
heliox tool close -- contact list --json
heliox tool close -- opportunity list --json
heliox tool close -- task list --json
```

### Search (Advanced Filtering: the entry point for finding records)

`search` POSTs a query body to `/data/search/`. Pass the query as JSON inline or
from a file with `@`. The body is forwarded verbatim, so the full query DSL is
available.

```bash
# find leads whose name contains "widgets"
heliox tool close -- search --data '{
  "query": {"type":"object_type","object_type":"lead",
            "related_query": {"type":"and","queries":[
              {"type":"field_condition","field":{"type":"regular_field","object_type":"lead","field_name":"display_name"},
               "condition":{"type":"text","mode":"contains","value":"widgets"}}]}},
  "_limit": 50
}' --json

heliox tool close -- search --data @query.json --json
```

### Write (create / update take a JSON body via `--data`)

```bash
# create a lead (the body is the Close lead payload; custom.<field_id> keys work)
heliox tool close -- lead create --data '{"name":"Widgets Inc","url":"widgets.com"}' --json
heliox tool close -- lead update <lead-id> --data '{"status_id":"stat_xxx"}' --json
heliox tool close -- lead delete <lead-id>

# contacts / opportunities follow the same shape
heliox tool close -- contact create --data '{"lead_id":"<lead-id>","name":"Jane Doe","emails":[{"email":"jane@x.com","type":"office"}]}' --json
heliox tool close -- opportunity create --data '{"lead_id":"<lead-id>","status_id":"stat_xxx","value":50000,"value_period":"one_time"}' --json
```

### Tasks

```bash
heliox tool close -- task create --data '{"lead_id":"<lead-id>","text":"Follow up next week","date":"2026-08-01"}' --json
heliox tool close -- task complete <task-id> --json      # marks is_complete=true
heliox tool close -- task delete <task-id>
```

### Activities (log and read interaction history)

Reads cover every activity type; writes ship `note-add` plus a generic
`create <type>` escape hatch.

```bash
# list activities (optionally scoped to one lead + type)
heliox tool close -- activity list --lead-id <lead-id> --type Note --json

# add a note
heliox tool close -- activity note-add --lead-id <lead-id> --note "Left a voicemail; will retry Thursday" --json

# log a call / email / any type via raw JSON (POST /activity/<type>/)
heliox tool close -- activity create call  --data '{"lead_id":"<lead-id>","direction":"outbound","note":"Quick sync"}' --json
heliox tool close -- activity create email --data '{"lead_id":"<lead-id>","status":"draft","subject":"Recap","body_text":"..."}' --json

# get / delete one by type + id
heliox tool close -- activity get note <activity-id> --json
heliox tool close -- activity delete note <activity-id>
```

Run `-- <resource> --help` (or `-- <resource> <verb> --help`) for exact flags
rather than guessing.

## Footguns

- **Custom fields go in `--data`, not flags.** Close custom fields are per-org
  (`custom.<field_id>` keys). The typed verbs expose no flags for them: put
  them in the `--data` JSON body on `create`/`update`.
- **`search` is the finder, not `list`.** `list` is a flat, paginated dump of a
  resource. To find records by name/email/stage/etc., build an Advanced
  Filtering query and use `search --data`.
- **A lead's activities are not in `lead get`.** `lead get` returns the lead
  with its contacts and opportunities, but **not** its activity history: use
  `activity list --lead-id <lead-id>`.
- **`task complete` only completes.** It sends `is_complete=true`; to change
  other task fields use `task update <id> --data '{...}'`.
- **`--account` when more than one Close account is connected.** A `409` lists
  the candidate account keys; re-run with `--account <key>` before the `--`.

## Safety

- Emails, calls, and tasks you create are visible to the user's whole Close
  team and can trigger outbound contact: follow the sensitive-operation rule in
  [../SKILL.md](../SKILL.md) before writing into a shared CRM.
- There is no undo for `delete`; confirm scope before removing a lead, contact,
  opportunity, task, or activity you did not create.
