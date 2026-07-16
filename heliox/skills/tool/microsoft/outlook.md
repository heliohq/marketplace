# Outlook (`heliox tool microsoft outlook -- ...`)

Read [microsoft.md](./microsoft.md) for auth and account selection. Everything
after `--` is the Outlook tool's own CLI, a faithful projection of Microsoft
Graph `/me/messages` and `/me/mailFolders`. Search passes OData through:
`--search '<text>'` (Graph `$search`) and `--filter '<OData>'`
(e.g. `isRead eq false`, `receivedDateTime ge 2026-07-01`).

## Core commands

```bash
# Triage / read
heliox tool microsoft outlook -- folders list                              # mailbox folders incl. exact unread counts
heliox tool microsoft outlook -- messages list --filter 'isRead eq false' --folder inbox --max 20 --json
heliox tool microsoft outlook -- messages list --search 'invoice' --max 20 --json
heliox tool microsoft outlook -- messages get <id> --body text --json       # body + attachment inventory (name, size)

# Attachments (land in your working directory; then use normal file/attachment flows)
heliox tool microsoft outlook -- messages attachments <id> --save ./inbox/

# Organize (reversible)
heliox tool microsoft outlook -- messages move <id>... --folder <id|wellKnownName>   # batched internally
heliox tool microsoft outlook -- messages mark <id>... --read        # also --unread / --flag / --unflag

# Reply / send / forward
heliox tool microsoft outlook -- messages reply <id> --body "Got it — results tomorrow."   # threading + quote handled; --all for reply-all
heliox tool microsoft outlook -- messages send --to a@b.com --subject "..." --body-file ./mail.md
heliox tool microsoft outlook -- messages forward <id> --to a@b.com --body "FYI"
```

Also available: `drafts create/list/get/update/send/delete`. (The connected
account's email is shown by `heliox tool list`, so there is no separate profile
command.)
Check `-- --help` rather than guessing flags. Every command takes `--json`;
lists default to a human-readable table with `--page <token>` for explicit
pagination (Graph `@odata.nextLink`).

## Sending email: default to the drafts flow

Sending leaves the user's own mailbox under their name — treat it like any
outward-facing sensitive action (see the safety rule in `../shared/SKILL.md`):

- **Default for anything non-trivial** (new recipients, external parties,
  commitments, attachments): create a draft, tell the user it is ready in their
  Outlook drafts, and only `drafts send <id>` after they confirm.

  ```bash
  heliox tool microsoft outlook -- drafts create --to boss@x.com --subject 'Weekly report' --body-file ./weekly.md --json
  ```

- Direct `messages send` / `reply` / `forward` is fine when the user explicitly
  asked you to send this specific message in this turn.

## Bulk operations: confirm the scale first

"Archive/move/mark them ALL" style requests can match huge numbers of messages.
Before any bulk `move`/`mark` affecting more than ~100 messages, report the
matched count and get the user's confirmation for that NUMBER — "move them all"
said casually rarely anticipates thousands. (Reversible or not, surprising
scale erodes trust.)

## Failure notes

- No connection → `heliox tool microsoft auth outlook`, relay the link.
- 409 with account candidates → re-run with `--account <key>`.
- 403 with a scope hint → the connection predates the needed scope; ask the
  user to disconnect and reconnect (fresh consent re-grants everything;
  `prompt=select_account` lets them re-pick the account).
- 401 reconnect required → refresh token revoked (password change / portal
  revoke); same reconnect path.
- Permanent delete is intentionally not exposed — there is no way to hard-delete
  a message; `move` to a folder is the reversible path.
