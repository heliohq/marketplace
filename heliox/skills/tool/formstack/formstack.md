# Formstack (`heliox tool formstack -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Formstack is a
**flat provider** (not grouped like `google`): everything after `--` is the
formstack tool's own CLI.

```bash
heliox tool formstack [--account <key>] -- <resource> <verb> [flags...]
```

Formstack is a form/survey builder — structured data *enters* an org through
forms. The tool wraps the Formstack **v2 (classic) REST API**; every command
prints the provider's JSON response verbatim on stdout. Resources: `form`,
`field`, `folder`, `submission`, `webhook`.

## The mental model (read this first)

- A **form** has **fields** (its questions, each with a numeric field id) and
  **submissions** (the responses). You almost always start by *finding the
  form*, then *reading its fields* to learn the field ids, then *pulling
  submissions* — response values are keyed by those field ids.
- The token carries the authorizing user's own in-app form permissions; there
  is **no scope selection** at connect time (access is all-or-nothing per that
  user).

## Core commands

### Find forms and read structure

```bash
heliox tool formstack -- form list --search "intake" --json      # search by name
heliox tool formstack -- form list --folder <folder-id> --page 1 --per-page 50 --json
heliox tool formstack -- folder list --json                       # locate a folder id
heliox tool formstack -- form get <form-id> --json                # form metadata + submission count + URL
heliox tool formstack -- form fields <form-id> --json             # the field ids you need to read/write responses
heliox tool formstack -- field get <field-id> --json
```

### Read submissions (responses)

```bash
# values are inlined by default (data=true); add --no-data for metadata only
heliox tool formstack -- submission list <form-id> --since 2026-07-01 --until "2026-07-21 23:59:59" --json
heliox tool formstack -- submission list <form-id> --search email=a@b.com --search status=paid --json
heliox tool formstack -- submission list <form-id> --sort DESC --page 2 --per-page 25 --json
heliox tool formstack -- submission get <submission-id> --json
```

- `--since`/`--until` map to `min_time`/`max_time` (`YYYY-MM-DD [HH:MM:SS]`,
  interpreted in **US/Eastern** by the API, not UTC).
- `--search field=value` is **repeatable** and maps to the API's paired
  `search_field_N`/`search_value_N` params; the `field` part is a form field id.
- For an encrypted form, pass `--encryption-password <pw>` (sent as the
  `X-FS-ENCRYPTION-PASSWORD` header) on `submission list` / `submission get`.

### Write

```bash
# submit on the user's behalf: --field id=value is repeatable → field_<id> params
heliox tool formstack -- submission create <form-id> --field 12345=Alice --field 12346=alice@x.com --json
heliox tool formstack -- submission delete <submission-id> --json

# stand up / duplicate a quick form
heliox tool formstack -- form create --name "RSVP" --folder <folder-id> --json
heliox tool formstack -- field create <form-id> --type email --label "Email" --required --json
heliox tool formstack -- field create <form-id> --type select --label "Plan" --options a,b,c --json
heliox tool formstack -- form copy <form-id> --json
heliox tool formstack -- form delete <form-id> --json        # soft delete per the API

# wire responses to an external URL
heliox tool formstack -- webhook list <form-id> --json
heliox tool formstack -- webhook create <form-id> --url https://example.com/hook --content-type json --json
heliox tool formstack -- webhook delete <webhook-id> --json
```

Common `field create --type` values: `text`, `textarea`, `email`, `number`,
`select`, `radio`, `checkbox`, `datetime`, `phone`, `name`. Advanced
layout/logic stays in the Formstack builder.

Run `-- <resource> --help` (or `-- <resource> <verb> --help`) for exact flags
rather than guessing.

## Footguns (where agents go wrong)

- **Submission values are keyed by field id, not label.** Read `form fields
  <form-id>` first to map a human label ("Email") to its numeric field id, then
  use that id in `--search email-field-id=...` and `submission create --field
  <id>=...`. `--field name=value` with a label instead of an id will not match.
- **Times are US/Eastern.** `--since`/`--until` are interpreted in the API's
  US/Eastern timezone, so an off-by-hours window is usually a timezone
  assumption, not a data gap.
- **`--search` is exact field=value pairing.** Each `--search` becomes one
  `search_field_N`/`search_value_N` pair (0-indexed); the API supports up to a
  handful of pairs. `--search novalue` with no `=` is a usage error.
- **`form delete` is a soft delete** per the API — it does not hard-purge.
  Editing a respondent's answers in place is deliberately unsupported; delete
  the submission and re-create if you truly must.
- **No scope prompt at connect.** The connection grants whatever the authorizing
  user can already do in Formstack; a missing form or action usually means that
  user lacks access, not a scope gap — reconnecting will not widen it.
- **`--account` when more than one Formstack account is connected.** A `409`
  lists candidate account keys; re-run with `--account <key>` before the `--`.

## Safety

- Creating submissions, deleting submissions/forms, and wiring webhooks are
  outward-facing or destructive — follow the sensitive-operation rule in
  [../SKILL.md](../SKILL.md) before running them, especially `submission
  delete` / `form delete` and any webhook that forwards response data off
  Formstack.
