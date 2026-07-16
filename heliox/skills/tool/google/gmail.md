# Gmail (`heliox tool google gmail -- ...`)

Read [google.md](./google.md) for auth and account selection. Everything
after `--` is the gmail tool's own CLI. `--query` takes Gmail's native search
syntax (`is:unread newer_than:7d from:alice has:attachment`).

## Core commands

```bash
# Counting: labels get gives EXACT totals in one call — never paginate to count,
# and never trust resultSizeEstimate (it saturates around ~100-201)
heliox tool google gmail -- labels get INBOX --json     # .messagesUnread = exact inbox unread count

# Triage / read
heliox tool google gmail -- messages list --query 'is:unread newer_than:1d' --max 20 --json
heliox tool google gmail -- messages get <id> --json          # body + attachment inventory
heliox tool google gmail -- threads get <thread-id> --json    # full conversation, read before replying

# Attachments (land in your working directory; then use normal file/attachment flows)
heliox tool google gmail -- messages attachments <id> --save ./inbox/

# Reply / send
heliox tool google gmail -- messages reply <id> --body "Got it — results tomorrow."   # threads + headers handled for you; --all for reply-all
heliox tool google gmail -- messages send --to a@b.com --subject "..." --body-file ./mail.md

# Organize (reversible)
heliox tool google gmail -- messages modify <id>... --archive --mark-read
heliox tool google gmail -- messages trash <id>...
```

Also available: `forward`, `drafts create/list/get/update/send/delete`,
`labels list/get/create`, `profile`. Check `-- --help` rather than guessing flags.

## Sending email: default to the drafts flow

Sending leaves the user's own mailbox under their name — treat it like any
outward-facing sensitive action:

- **Default for anything non-trivial** (new recipients, external parties,
  commitments, attachments): create a draft, tell the user it is ready in
  their Gmail drafts, and only `drafts send <id>` after they confirm.

  ```bash
  heliox tool google gmail -- drafts create --to boss@x.com --subject 'Weekly report' --body-file ./weekly.md --json
  ```

- Direct `messages send` / `reply` is fine when the user explicitly asked you
  to send this specific message in this turn.

## Bulk operations: confirm the scale first

"Archive/label/trash them ALL" style requests can match tens of thousands of
messages. Before any bulk modify/trash affecting more than ~100 messages,
report the matched count and get the user's confirmation for that NUMBER —
"archive them all" said casually rarely anticipates 20,000. (Reversible or
not, surprising scale erodes trust.)

## Failure notes

- **Never report `resultSizeEstimate` as a count** — it is Gmail's cheap index
  estimate and saturates (~100-201) regardless of the true total. Its only
  reliable reading is zero vs non-zero. Exact counts: `labels get <id>` for
  label-level totals; otherwise paginate to the end and sum.
- `messages get` on huge threads: prefer `threads get` once over N `messages get` calls.
- 403 with a scope hint → the connection predates the needed scope; ask the
  user to reconnect (fresh consent re-grants everything).
- Attachments larger than the 25MB Gmail limit cannot be sent via `--attach`;
  say so instead of retrying.
