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
| gmail | [gmail.md](./gmail.md) | Search, read, send, reply, organize the user's mailbox; fetch attachments |
