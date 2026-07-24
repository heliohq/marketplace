# Salesloft (`heliox tool salesloft -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Salesloft is a
**flat provider**: everything after `--` is the Salesloft tool's own CLI,
speaking Salesloft REST API v2 with the connected account's OAuth token.

```bash
heliox tool salesloft [--account <key>] -- <resource> <verb> [flags...]
```

Resources: `me`, `user`, `person`, `account`, `cadence`, `task`, `note`,
`activity`, `email`, `call`. Run `-- <resource> --help` (or
`-- <resource> <verb> --help`) for the full flag surface.

## What it is for

Salesloft is a sales-engagement platform. As an SDR/AE assistant you will:
look up and maintain prospects (`person`) and accounts (`account`), drive
outreach sequences (`cadence`), manage the rep's task queue (`task`), log
context (`note`), and review what has happened (`activity` / `email` / `call`).

## Output shape (learn once, applies to every command)

Responses pass Salesloft's envelope through verbatim: a `data` object (single
resource) or `data` array (lists), plus `metadata.paging` on lists with
`current_page` / `next_page` / `total_pages` / `total_count`. Page with
`--page` and `--per-page` (max 100).

## Reading (prefer incremental over deep paging)

```bash
heliox tool salesloft -- me                                   # who am I / sanity check
heliox tool salesloft -- person list --email jane@acme.com    # find a prospect by email first
heliox tool salesloft -- person get --id 42
heliox tool salesloft -- cadence list                         # discover cadences to enroll into
heliox tool salesloft -- task list --filter current_state=scheduled
```

The rate limit is **600 cost/minute shared across the whole team**, and deep
pages (beyond page 100) cost extra. For "what changed since last time", poll by
update time instead of walking every page:

```bash
heliox tool salesloft -- person list --updated-since 2026-07-01T00:00:00Z --sort-by updated_at --sort-direction ASC
```

`--updated-since` maps to Salesloft's `updated_at[gte]` filter and is available
on every `list`. For any documented filter the tool does not expose as a named
flag, use `--filter key=value` (repeatable; the value is sent verbatim, so
array filters look like `--filter "person_stage_id[]=7"`).

## Enrolling a prospect into a cadence (the core write)

```bash
heliox tool salesloft -- cadence add-person --person-id 11 --cadence-id 22 [--user-id 33]
```

`--user-id` defaults to the authenticated user; set it to assign a different
rep on the team. Check enrollment state with:

```bash
heliox tool salesloft -- cadence memberships --person-id 11 --cadence-id 22
```

## Creating and updating records

Write verbs (`person create|update`, `account create|update`, `task
create|update`, `note create`) take named flags for the common fields:

```bash
heliox tool salesloft -- person create --email jane@acme.com --first-name Jane --last-name Doe --title "VP Sales" --account-id 77
heliox tool salesloft -- task create --subject "Follow up" --task-type call --person-id 11 --due-date 2026-08-01 --current-state scheduled
heliox tool salesloft -- task update --id 8 --current-state completed        # complete a task
heliox tool salesloft -- note create --content "Left a voicemail" --associated-with-type person --associated-with-id 11
```

For any field the named flags do not cover, pass a raw JSON body with `--body`;
its keys override the named flags for full request fidelity:

```bash
heliox tool salesloft -- person update --id 5 --body '{"custom_fields":{"Region":"EU"}}'
```

Salesloft ids are integers — pass them bare (e.g. `--account-id 77`), not
quoted.

## Footguns

- **Team-shared rate budget**: other integrations on the same Salesloft team
  share the 600 cost/min. Prefer `--updated-since` polling over re-walking
  large lists, and keep `--per-page` at or below 100.
- **Find before you write**: `person list --email` to resolve a prospect before
  emailing or enrolling — creating a person on a duplicate email is a common
  mistake.
- **Updates are PUT and partial**: only the fields you pass (named or via
  `--body`) are sent; unset fields are left untouched.
- **No deletes**: this tool intentionally omits destructive delete verbs.

## Safety

Enrolling a person into a cadence, creating or updating people/accounts,
creating tasks, and adding notes all change the rep's live Salesloft workspace
and can trigger outreach to prospects. Treat cadence enrollment and any
record write as outward-facing actions: follow the sensitive-operation rule in
[../SKILL.md](../SKILL.md) — confirm with the user before the
first cadence enrollment or record write in a session, and never enroll a
prospect the user has not sanctioned.
