# Fillout (`heliox tool fillout -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Fillout is a
**flat provider** (not grouped like `google`): everything after `--` is the
fillout tool's own CLI.

```bash
heliox tool fillout [--account <key>] -- <resource> <verb> [flags...]
```

Fillout is a form builder. This tool reads the account's **forms** and their
**submissions** (responses), and manages the **webhooks** that notify you of new
responses. Output is Fillout's own JSON, passed through verbatim.

## Identity: one Fillout account per assistant

Fillout OAuth returns no per-account identifier, so a connection is **one
Fillout account, single per assistant** — there is no account picker and
`--account` is rarely needed. The correct API host (US / EU data-residency /
self-host) is captured at connect time and injected automatically; you never
pass a base URL.

## Commands

### Forms

```bash
# list every form in the account
heliox tool fillout -- form list

# one form's metadata + its question/field schema (needed to interpret answers)
heliox tool fillout -- form get <formId>
```

### Submissions (responses)

```bash
# list a form's submissions, newest first, only finished ones, matching "acme"
heliox tool fillout -- submission list <formId> \
  --status finished --sort desc --search acme --limit 50

# one submission by id
heliox tool fillout -- submission get <formId> <submissionId> --include-edit-link

# create submission(s) — body is Fillout's own JSON, from --data or --file
heliox tool fillout -- submission create <formId> \
  --data '{"submissions":[{"questions":[{"id":"<qid>","value":"Hello"}]}]}'

# delete a submission
heliox tool fillout -- submission delete <formId> <submissionId>
```

`submission list` filters (all optional, pass-through to Fillout): `--limit`
(1–150, default 50), `--offset`, `--status finished|in_progress`, `--after-date`
/ `--before-date` (ISO date-time), `--sort asc|desc`, `--search <text>`,
`--include-edit-link`, `--include-preview`.

### Webhooks

```bash
# register a webhook on a form for new submissions
heliox tool fillout -- webhook create --form-id <formId> --url https://example.com/hook

# remove a webhook (id comes from the create response)
heliox tool fillout -- webhook delete --webhook-id <id>
```

## Footguns

- **Interpret answers via the schema.** A submission's `questions[]` carry
  question ids and values; run `form get <formId>` first to map ids to the
  human question text and types.
- **API-created submissions are quiet.** Fillout does not fire email
  notifications, workflows, or integrations for submissions you create via API.
- **`submission create` body is verbatim.** The tool validates it is JSON and
  passes it through — it does not reshape it. The top level is
  `{"submissions":[ ... ]}` (max 10), each item requiring a `questions` array.
