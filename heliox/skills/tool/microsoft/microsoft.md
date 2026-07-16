# Microsoft tools (`heliox tool microsoft ...`)

Read [../SKILL.md](../SKILL.md) first for the general connect/use model.
Microsoft products are connected **per app** — each app is its own connection
with its own consent (a separate Entra app registration behind the scenes).
Per-app details live in this directory; run `heliox tool microsoft --help` for
the current app list.

All apps go through `login.microsoftonline.com` and support both personal
Microsoft accounts (Outlook.com) and work/school accounts.

## Auth (per app)

```bash
heliox tool microsoft auth outlook     # mint the authorize link, relay to the user
heliox tool microsoft auth calendar
heliox tool microsoft auth onedrive
```

Connecting one app grants nothing for the others — if a task needs Outlook mail
and OneDrive files, each needs its own auth link and user consent. The consent
screen lets the user pick which Microsoft account to sign in with.

## Accounts

One connection acts as the user's own Microsoft account for that app. The user
may connect several accounts of the same app; disambiguate calls with
`--account <key>` (keys come from `heliox tool list` or the 409 candidate
list). `--account` goes **before** the `--` separator:

```bash
heliox tool microsoft outlook --account work@corp.com -- messages list --max 10
```

## Command shape

The subcommand after `microsoft` is the group-scoped app command (`outlook` /
`calendar` / `onedrive`), which differs from the internal tool id. You never
type the tool id — always use the subcommand:

```bash
heliox tool microsoft auth <app>              # connect
heliox tool microsoft <app> [--account <key>] -- <tool args...>   # use
```

## Apps

| App | Reference | What it does |
| --- | --- | --- |
| outlook | [outlook.md](./outlook.md) | Search, read, send, reply, organize the user's Outlook mailbox; fetch attachments |
| calendar | [calendar.md](./calendar.md) | Read/manage the user's Outlook calendar; create, change, cancel events; respond to invites |
| onedrive | [onedrive.md](./onedrive.md) | Browse, search, download, upload OneDrive files; create folders; share links |

## Disconnect note

Disconnect is **local only**: it removes Helio's stored credential and the
connection row, but Microsoft has no revoke endpoint, so the authorization is
**not** revoked on Microsoft's side. When telling the user a tool is
disconnected, add that to fully remove access they should visit
`account.microsoft.com` / `myapps.microsoft.com`.
