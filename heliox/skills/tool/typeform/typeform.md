# Typeform (`heliox tool typeform -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Typeform is a
**flat provider** (not grouped like `google`): everything after `--` is the
typeform tool's own CLI.

```bash
heliox tool typeform [--account <key>] -- <resource> <verb> [flags...]
```

Commands are grouped by resource: `me`, `form`, `response`, `workspace`,
`webhook`. Every command prints the provider's own JSON on success; pass
`--json` for the structured error envelope on failure. Run
`-- <resource> <verb> --help` for exact flags rather than guessing.

## The mental model (read this first — it prevents the #1 footgun)

A **response** is a list of `answers`, and each answer identifies its question
only by a **field `id`/`ref`** — not by the question's visible title. To make
sense of responses you almost always need the form's **field dictionary**
first:

```bash
heliox tool typeform -- form get <form_id> --json      # field ids, refs, types, choice labels
heliox tool typeform -- response list <form_id> --json  # answers[].field.{id,ref,type} + values
```

Join `answers[].field.ref` (or `.id`) against the form's `fields[]` to label
each answer. `response list` does **not** flatten or resolve titles for you.

## Core commands

### Read responses (the dominant job)

```bash
# newest first, one page (page size max 1000); the agent drives the cursor
heliox tool typeform -- response list <form_id> --page-size 200 --sort submitted_at,desc --json

# date window — the timestamp filtered depends on --response-type (see Footguns)
heliox tool typeform -- response list <form_id> --since 2026-01-01T00:00:00 --until 2026-02-01T00:00:00 --json

# partial + completed submissions, text search, only specific fields
heliox tool typeform -- response list <form_id> --response-type partial,completed --query "refund" --fields <ref1>,<ref2> --json

# page forward with the token cursor from a prior page's items
heliox tool typeform -- response list <form_id> --after <response_token> --json
```

### Find and inspect forms

```bash
heliox tool typeform -- form list --search "NPS" --workspace-id <ws> --page-size 50 --sort-by last_updated_at --order-by desc --json
heliox tool typeform -- form get <form_id> --json
```

### Author / edit forms

```bash
# create from a full form-definition JSON (inline or @file)
heliox tool typeform -- form create --definition @survey.json --json

# PUT full overwrite — the ONLY way to change questions/fields
heliox tool typeform -- form update <form_id> --definition @survey.json --json

# PATCH metadata only — JSON-Patch ops on /title, /theme, /workspace, /settings/*
heliox tool typeform -- form patch <form_id> --patch '[{"op":"replace","path":"/title","value":"New title"}]'

heliox tool typeform -- form delete <form_id>
```

### Workspaces (so form creation lands in the right place)

```bash
heliox tool typeform -- workspace list --search "Team" --json
heliox tool typeform -- workspace get <workspace_id> --json
heliox tool typeform -- workspace create --name "Q3 Surveys" --json
```

### Webhooks (deliver new responses somewhere)

```bash
heliox tool typeform -- webhook list <form_id> --json
heliox tool typeform -- webhook get <form_id> <tag> --json
# create-or-update by tag (upsert)
heliox tool typeform -- webhook set <form_id> <tag> --url https://example.com/hook --enabled --secret <s> --json
heliox tool typeform -- webhook delete <form_id> <tag>
```

### Identity

```bash
heliox tool typeform -- me --json     # alias / email / language of the connected account
```

## Footguns (the important part — these are where agents go wrong)

- **Answers are keyed by field id/ref, not title.** `response list` gives you
  `answers[].field.{id,ref,type}` and a typed value — never the question text.
  Run `form get <form_id>` and join on `field.ref` to label answers. Skipping
  this is the #1 mistake.
- **`--response-type` changes which timestamp the date window filters.**
  `--since`/`--until` filter `submitted_at` for `completed` (the default),
  `staged_at` for `partial`, and `landed_at` for `started`. If you want a date
  window over partials, you must pass `--response-type partial` or the window
  silently filters the wrong timestamp.
- **Cursors and `--sort` don't mix.** `--after`/`--before` force processing
  order; combining either with `--sort` is a `400` from Typeform. Use one or the
  other.
- **`form patch` can't touch questions.** PATCH is a JSON-Patch ops array
  restricted to `/title`, `/theme`, `/workspace`, `/settings/*`. To add, remove,
  or edit fields/questions use **`form update`** (PUT full overwrite) — send the
  complete definition, not a partial.
- **Very recent responses may be missing.** Responses from roughly the last
  30 minutes may not appear yet — an empty window is not proof of "no
  responses". For real-time delivery, wire a `webhook set` instead of polling.
- **Rate limit is ~2 requests/second per token.** A `429`/`RATE_LIMITED` is
  surfaced verbatim; back off and retry rather than looping.
- **EU-hosted accounts are not supported in v1.** This tool targets the global
  `api.typeform.com` base URL. An account homed in Typeform's EU data center
  will return no data through it — reconnect is not a fix; EU support is a
  planned follow-up.
- **`--account` when more than one Typeform account is connected.** A `409`
  lists the candidate account keys; re-run with `--account <key>` (before the
  `--`).

## Safety

- `form create/update/patch/delete`, `workspace create`, and `webhook
  set/delete` mutate the user's Typeform account — follow the
  sensitive-operation rule in [../SKILL.md](../SKILL.md) before running one, and
  prefer confirming a `form delete` / `form update` (full overwrite) against a
  form you did not create.
- A webhook `--url`/`--secret` sends live submission data off to a third
  endpoint; confirm the destination before wiring it.
- Never echo tokens; the CLI injects them for you and never shows them.
