# Google tools (`heliox tool google ...`)

Read [../SKILL.md](../SKILL.md) first for the general connect/use model.
Google products are connected **per app** — each app is its own connection
with its own consent. Per-app details live in this directory
([gmail.md](./gmail.md) today); run `heliox tool google --help` for the
current app list (drive / calendar may join later, each as its own file here).

## Auth (per app)

```bash
heliox tool google auth gmail --json    # mint the authorize link, relay to the user
```

Connecting one app grants nothing for the others — if a task needs Gmail and
(later) Drive, each needs its own auth link and user consent.

## Accounts

One connection acts as the user's own Google account for that app. The user
may connect several accounts of the same app; disambiguate calls with
`--account <key>` (keys come from `heliox tool list` or the 409 candidate
list). `--account` goes **before** the `--` separator:

```bash
heliox tool google gmail --account work@corp.com -- messages list --max 10
```

## Apps

| App | Reference | What it does |
| --- | --- | --- |
| analytics | [analytics.md](./analytics.md) | GA4 read-only reporting — traffic, engagement, and conversion reports plus realtime; discover property ids and valid metric/dimension names |
| calendar | [calendar.md](./calendar.md) | Create, list, update, and delete events; check free/busy; read-only list of your calendars |
| contacts | [contacts.md](./contacts.md) | Search and read the user's contacts (read-only — can't create or edit them) |
| docs | [docs.md](./docs.md) | Create, read, and edit Google Docs; insert and format text content |
| drive | [drive.md](./drive.md) | Work with files this tool creates or opens — read, update, and share those; not full-library browse or search |
| forms | [forms.md](./forms.md) | Create forms, add and edit questions, read submitted responses |
| gmail | [gmail.md](./gmail.md) | Search, read, send, reply, organize the user's mailbox; fetch attachments |
| meet | [meet.md](./meet.md) | Create ad-hoc meeting links and change space config; post-meeting participants, transcripts, recordings index |
| sheets | [sheets.md](./sheets.md) | Read, write, append, and clear spreadsheet values by link/ID; create spreadsheets and manage tabs — no list/search (work from a link the user gives you) |
| slides | [slides.md](./slides.md) | Create presentations; add and edit slides, text, and images |
| tasks | [tasks.md](./tasks.md) | Manage the user's task lists and tasks — create, list, update, and complete |
