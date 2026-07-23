# Pipedrive (`heliox tool pipedrive -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Pipedrive is a
**flat provider** (not grouped like `google`): everything after `--` is the
pipedrive tool's own CLI.

```bash
heliox tool pipedrive [--account <key>] -- <resource> <verb> [flags...]
```

Pipedrive is a sales CRM. You work deals through a pipeline, maintain the
people and organizations behind them, log and schedule activities, capture
leads, and leave notes. Output is the provider's JSON response **verbatim** on
stdout; failures print Pipedrive's own error text on stderr and exit non-zero.

## Command surface

```
pipedrive deal      list | get <id> | create | update <id> | search --term <q>
pipedrive person    list | get <id> | create | update <id> | search --term <q>
pipedrive org       list | get <id> | create | update <id> | search --term <q>
pipedrive activity  list | get <id> | create | update <id> | delete <id>
pipedrive lead      list | get <id> | create | update <id> | delete <id>
pipedrive note      list | get <id> | add    | update <id> | delete <id>
pipedrive pipeline  list | get <id>                         # read-only
pipedrive stage     list | get <id>                         # read-only
pipedrive user      me | list
pipedrive search    --term <q> [--types deal,person,organization,lead]
```

Run `-- <resource> <verb> --help` for the exact flags rather than guessing.

## The mental model (read this first)

- **A deal moves through stages inside a pipeline.** Read the pipeline's stages
  with `stage list --pipeline-id <id>`, then move a deal by patching its
  `--stage-id`. You do **not** delete deals — you close them: `deal update <id>
  --status won`, or `--status lost --lost-reason "..."`.
- **Leads are not deals.** A lead is an unqualified, pre-pipeline record; when
  it qualifies it becomes a deal. Capture inbound interest as a `lead`; track
  an active sales opportunity as a `deal`.
- **Notes attach to a record.** Log context with `note add --content "..."` plus
  exactly the link you mean (`--deal-id`, `--person-id`, `--org-id`, or
  `--lead-id`).

## Core commands

### Read + search

```bash
# list with filters; v2 lists page by CURSOR (see Pagination)
heliox tool pipedrive -- deal list --status open --pipeline-id 1 --limit 100
heliox tool pipedrive -- deal list --cursor <next_cursor>          # next page

heliox tool pipedrive -- deal get 42
heliox tool pipedrive -- stage list --pipeline-id 1               # interpret/move deals
heliox tool pipedrive -- pipeline list

# entity search (one type) vs cross-entity search (many types)
heliox tool pipedrive -- deal search --term "Acme renewal"
heliox tool pipedrive -- search --term "Acme" --types deal,person,organization
```

### Write

```bash
# create: typed flags cover the common fields
heliox tool pipedrive -- deal create --title "Acme renewal" --value 12000 --currency USD --person-id 7

# update is a PARTIAL patch — only the flags you set change
heliox tool pipedrive -- deal update 42 --stage-id 3                 # move a stage
heliox tool pipedrive -- deal update 42 --status won                 # close won
heliox tool pipedrive -- deal update 42 --status lost --lost-reason "Chose competitor"

# people / orgs
heliox tool pipedrive -- person create --name "Jane Doe" --org-id 5
heliox tool pipedrive -- org update 5 --name "Acme Inc."

# activities (calls, meetings, tasks)
heliox tool pipedrive -- activity create --subject "Discovery call" --type call --due-date 2026-07-25 --deal-id 42
heliox tool pipedrive -- activity update 9 --done                   # mark complete

# leads + notes
heliox tool pipedrive -- lead create --title "Inbound: Acme" --person-id 7
heliox tool pipedrive -- note add --content "Left a voicemail" --deal-id 42
```

### The `--data` escape hatch

Typed flags cover the high-traffic fields. For any field they don't expose
(custom fields, nested objects like a lead's `value`), pass raw JSON with
`--data`; typed flags overlay it, so you can combine both:

```bash
heliox tool pipedrive -- lead create --title "Inbound" --data '{"value":{"amount":5000,"currency":"USD"}}'
```

## Pagination (the #1 thing to get right)

- **v2 resources — deals, persons, orgs, activities, pipelines, stages, and
  every `search` — page by CURSOR.** The response's
  `additional_data.next_cursor` is an opaque string; pass it back as `--cursor`
  to get the next page. When `next_cursor` is `null`, you're at the end. Use
  `--limit` (max 500 on lists, 100 on search) to size a page.
- **v1 resources — leads, notes — page by OFFSET.** Use `--start <n>` +
  `--limit`; `additional_data.pagination` tells you `more_items_in_collection`.
- **users** returns everyone in one call (no pagination).

Don't invent a `--page` flag — it doesn't exist. Read the cursor/offset out of
the verbatim response and feed it back.

## Footguns

- **Deals are closed, not deleted.** There is no `deal delete` (nor person/org
  delete) — by design. Close a deal with `--status won|lost`; a `lost` deal
  should carry `--lost-reason`.
- **`update` is a partial patch.** Only the flags you pass are sent. Omit a
  field to leave it untouched — you never need to re-send the whole record.
- **Stage ids are pipeline-specific.** A `--stage-id` only makes sense within
  its pipeline; read `stage list --pipeline-id <id>` before moving a deal so you
  patch a stage that belongs to that deal's pipeline.
- **Leads use UUID ids; deals/persons/orgs/activities use integer ids.** A
  lead's `note --lead-id` takes the UUID string.
- **Boolean flags are bare, never space-separated.** `--done` and
  `--exact-match` take no value: write `--done` (or `--done=true`), never
  `--done true`. A trailing `true` is parsed as a second positional argument and
  the command fails with `accepts 1 arg(s), received 2` before it reaches the
  API.
- **`search` term needs ≥2 characters.** A 1-character term is rejected unless
  you also pass `--exact-match`.
- **`--account <key>` when more than one Pipedrive company is connected.** A
  `409` lists the candidate account keys (each is the company's API domain);
  re-run with `--account <key>` before the `--`.

## Safety

- Creating/updating deals, activities, notes, and closing deals mutates the
  user's live CRM that their whole team sees — follow the sensitive-operation
  rule in [../SKILL.md](../SKILL.md) before writing, especially bulk changes or
  closing a deal `lost`.
