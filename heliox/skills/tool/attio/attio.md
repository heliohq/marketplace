# Attio (`heliox tool attio -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Attio is a
**flat provider** (not grouped like `google`): everything after `--` is the
attio tool's own CLI.

```bash
heliox tool attio [--account <key>] -- <resource> <verb> [flags...]
```

Attio is a **data-model-first CRM**. A workspace holds **objects** (standard:
`people`, `companies`, `deals`, `users`, `workspaces`; plus custom objects),
each object holds **records**, and **lists** overlay records as pipelines with
per-list **entries**. Notes, tasks, threads and comments attach to records.

## The mental model (read this first — it prevents the #1 footgun)

Attio schemas are **per-workspace**: object slugs, attribute slugs, and
select/status options differ between workspaces and can be customised. **Never
hardcode attribute slugs.** Discover the schema first, then build the write
payload:

```bash
heliox tool attio -- object list --json                       # what objects exist (incl. custom)
heliox tool attio -- attribute list --object people --json    # what attributes (slugs) an object has
heliox tool attio -- attribute options --object deals --attribute stage --json   # select options
heliox tool attio -- attribute statuses --object deals --attribute stage --json  # status stages
```

Record/entry attribute **values** are structured (arrays of typed value
objects), so writes take **raw JSON** via `--values` rather than a flag per
attribute. `--json` on any command emits Attio's response verbatim (`{"data":
...}`) so you can chain calls; omit it for a compact one-line-per-item summary.

## Core commands

### Identity & discovery

```bash
heliox tool attio -- whoami --json                            # token's workspace identity
heliox tool attio -- object list --json | object get <object> --json
heliox tool attio -- list list --json   | list get <list> --json
heliox tool attio -- member list --json | member get <member_id> --json   # resolve assignees/authors
```

### Find & read records

```bash
# fuzzy search — defaults to people,companies (the two always-present objects)
heliox tool attio -- record search --query "Acme" --json
# broaden to more/custom objects explicitly (slugs from `object list`)
heliox tool attio -- record search --query "Acme" --objects people,companies,deals --json
# scope visibility to one member (id or email)
heliox tool attio -- record search --query "Acme" --request-as-member alice@acme.com --json

# exact filter/sort query of one object (filter/sorts are raw Attio-wire JSON)
heliox tool attio -- record query deals --filter '{"stage":"Won"}' --sorts '[{"attribute":"created_at","direction":"desc"}]' --limit 25 --json

heliox tool attio -- record get people <record_id> --json
```

### Write records

```bash
heliox tool attio -- record create people --values '{"name":"Ada Lovelace","email_addresses":["ada@x.com"]}' --json

# update DEFAULTS to overwrite (PUT): the values you send REPLACE what's there
heliox tool attio -- record update people <record_id> --values '{"job_title":"CTO"}' --json
# --append switches to PATCH: multiselect values are ADDED, not replaced
heliox tool attio -- record update people <record_id> --values '{"tags":["vip"]}' --append --json

# upsert (assert) by a unique matching attribute — create if absent, overwrite if present
heliox tool attio -- record upsert people --values '{"email_addresses":["ada@x.com"],"name":"Ada"}' --match email_addresses --json

heliox tool attio -- record delete people <record_id> --json
```

### Lists & pipeline entries

```bash
heliox tool attio -- entry query <list> --filter '<json>' --sorts '<json>' --limit 50 --json
heliox tool attio -- entry add <list> --parent-record <record_id> --parent-object people --values '{"stage":"Lead"}' --json
heliox tool attio -- entry get <list> <entry_id> --json
# entry update mirrors record update: default overwrite (PUT), --append for PATCH
heliox tool attio -- entry update <list> <entry_id> --values '{"stage":"Won"}' --json
heliox tool attio -- entry remove <list> <entry_id> --json
```

### Notes, tasks, threads, comments

```bash
# notes — exactly one of --markdown / --plaintext
heliox tool attio -- note create --parent people:<record_id> --title "Call recap" --markdown "# Notes\n..." --json
heliox tool attio -- note list --record people:<record_id> --json
heliox tool attio -- note get <note_id> --json  |  note delete <note_id> --json

# tasks — content is plaintext; deadline is ISO 8601; assignee/record optional
heliox tool attio -- task create --content "Send proposal" --deadline 2026-02-01T15:00:00Z --assignee <member_id> --record people:<record_id> --json
heliox tool attio -- task list --record people:<record_id> --json
heliox tool attio -- task update <task_id> --completed true --json
heliox tool attio -- task delete <task_id> --json

# threads (read) and comments (write) — comment target is one of --thread / --record
heliox tool attio -- thread list --record people:<record_id> --json  |  thread get <thread_id> --json
heliox tool attio -- comment create --record people:<record_id> --content "Following up" --json
heliox tool attio -- comment create --thread <thread_id> --content "Reply" --json
```

Run `-- <resource> <verb> --help` for the exact flags rather than guessing.

## Footguns (the important part — these are where agents go wrong)

- **Discover the schema before any write.** Attribute slugs, select options and
  status stages are per-workspace. Build `--values` from `attribute list` /
  `attribute options` / `attribute statuses`, not from memory — a wrong slug is
  a `400`.
- **`record update` overwrites by default.** The default verb is PUT: the values
  you send **replace** existing ones (multiselect values are removed and reset).
  To *add* to a multiselect without dropping the current values, pass
  `--append` (PATCH). Same rule for `entry update`.
- **`record search` defaults to `people,companies` only.** Those two objects are
  the only ones present in every workspace; `deals`/`users`/`workspaces` are
  optional and may be disabled, and searching a disabled slug is a `400`
  (`value_not_found`). To search other/custom objects, name them explicitly with
  `--objects` (discover slugs via `object list`).
- **Comments need a workspace-member author.** `comment create` defaults the
  author to the connected token's member (`whoami`'s
  `authorized_by_workspace_member_id`) and always sends `format: plaintext`. If
  the token isn't tied to a member it fails fast asking for `--author
  <member_id>` — resolve one via `member list`.
- **`--parent` / `--record` are `<object>:<record_id>`.** Notes use `--parent`,
  tasks/threads/comments use `--record`; both take the `object:record_id` shape
  (e.g. `people:abc-123`). A missing colon is a usage error.
- **Pagination differs by endpoint.** `record query` / `entry query` take
  `--limit` / `--offset` in the request body; list-style reads (`note list`,
  `task list`, `attribute list`, …) take them as query params; `record search`
  takes `--limit` only (max 25, no offset). The flags are surfaced verbatim —
  nothing auto-paginates.
- **`--account` when more than one Attio workspace is connected.** A `409` lists
  the candidate account keys; re-run with `--account <key>` (before the `--`).

## Safety

- Notes, comments and pipeline changes are visible to everyone in the Attio
  workspace — follow the sensitive-operation rule in [../SKILL.md](../SKILL.md)
  before writing into a workspace others read.
- Schema introspection (`object` / `attribute`) is read-only; the tool cannot
  create or alter objects/attributes, only records, entries, notes, tasks and
  comments.
