# Google Forms (`heliox tool google forms -- ...`)

Read [google.md](./google.md) for auth and account selection. Everything after
`--` is the forms tool's own CLI. A `<form-id>` argument accepts either the bare
id or an **edit** link (`https://docs.google.com/forms/d/<id>/edit`) — the tool
extracts the id. A **responder** link (`/forms/d/e/…/viewform`) carries a
different id and is rejected; ask the user for the edit link.

There is **no "list my forms"** command (the Forms API has no list method, and
listing needs a restricted Drive scope this tool does not hold). Get the formId
from the user's edit link or from a form you just created.

## The minimal loop: create → build → review → publish → share

Forms are created **unpublished**. Building the questions, publishing, and
sharing are separate, explicit steps — this is the soft guardrail, not a
limitation to work around.

```bash
# 1. Create an empty, unpublished form (title only)
heliox tool google forms -- create --title "Team offsite poll" --json   # returns formId

# 2. Add questions with batch-update (faithful Forms API Request[] JSON)
heliox tool google forms -- batch-update <form-id> --requests '[
  {"createItem":{
     "item":{"title":"Which day works?","questionItem":{"question":{
       "required":true,
       "choiceQuestion":{"type":"RADIO","options":[{"value":"Fri"},{"value":"Sat"}]}}}},
     "location":{"index":0}}}
]'
# For anything larger, write the JSON to a file and use --requests-file ./reqs.json

# 3. Show the structure + edit link to the USER and get their OK before publishing
heliox tool google forms -- get <form-id>

# 4. Publish (starts accepting responses) — only after the user confirms
heliox tool google forms -- publish <form-id>

# 5. Share so people can answer
heliox tool google forms -- responders add <form-id> --to alice@x.com,bob@y.com
```

`batch-update` is the only payload you actually author; `createItem` /
`updateItem` / `deleteItem` / `moveItem` / `updateFormInfo` / `updateSettings`
are the Request union the API already documents. Pass an array (`[ ... ]`) or a
full `{"requests":[ ... ]}` body — either works.

## Soft guardrail: confirm before anything outward-facing

Publishing a form and sharing it collects data from real people under the
user's name. Treat publish and responder sharing as sensitive outward actions:

- **Default flow**: create (unpublished) → batch-update → `get` and show the
  user the structure + edit link → publish **only after they confirm**.
- **`responders add --anyone` makes the form answerable by anyone with the
  link.** Confirm this *specific* public-exposure fact with the user **every
  time** — never make a form public on a casual "share it".
- Reversible fallbacks: a form built by mistake is harmless while unpublished;
  `unpublish` takes a live form fully offline, `close` stops new responses
  while keeping it published, `reopen` resumes.

## Reading structure and responses

```bash
heliox tool google forms -- get <form-id> --json                 # structure, publishSettings, responderUri, linkedSheetId
heliox tool google forms -- responses list <form-id> --json      # answers as native JSON — summarize/analyze directly
heliox tool google forms -- responses list <form-id> --filter 'timestamp >= 2026-07-01T00:00:00Z'   # incremental pull
heliox tool google forms -- responses get <form-id> <response-id> --json
heliox tool google forms -- responders list <form-id>            # who can answer; whether anyone-with-link is on
```

## Editing a live form

`batch-update` on a form that already has responses does **not** touch stored
answers, but it changes what future responders see. Before editing a live form
(especially `deleteItem`), run `get` first, and tell the user the impact.

## Capability boundaries

- **publish / responders \*** only work on forms **this assistant created**
  (the `drive.file` scope does not reach the user's pre-existing forms). On a
  form the user made in the Forms UI, the tool returns a 403/404 and says so —
  direct the user to the Publish panel in the Forms UI. `get` and `responses`
  are unaffected (they work on any form the user can access).
- **No response count endpoint**: to count responses, paginate `responses list`
  with `--page-token` to the end and sum. For a large form, tell the user the
  scale first.
- **No proactive wakeup** on new responses: only poll (`responses list --filter
  'timestamp >= …'` for incremental pulls) when the user explicitly asks.
- File-upload questions can be read but not created via the API.
- Want responses in a spreadsheet, or an email when results land? Those are
  other tools (`heliox tool google sheets` to write the responses into a sheet;
  the gmail tool to send results) — combine them, don't reach for a Drive scope
  here.

Check `-- --help` (or `<group> --help`) rather than guessing flags.
