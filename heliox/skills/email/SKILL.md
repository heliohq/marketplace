---
name: email
description: "Use `heliox email ...` for the AI user's email inbox and outbound mail: listing recent emails, waiting for verification emails, reading a message, sending new mail, replying within a thread, or handling email-based auth and vendor flows. Trigger whenever the assistant needs to read its own inbox, wait for an inbound mail (signup verification, OTP, vendor reply), send mail to a third party, or reply within an existing email thread — this is the only path; the runtime has no separate mail client."
user-invocable: false
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox email --help"
---

# Heliox Email

Start by reading `../shared/SKILL.md`.

Email commands operate as the authenticated AI user unless `--ai-user-id` overrides it.

## List and read

```bash
heliox email list --json
heliox email list --limit 10 --json
heliox email list --ai-user-id <ai_user_id> --json
heliox email read <email_id> --json
heliox email read <email_id> --format text
heliox email read <email_id> --format html
heliox email read <email_id> --format raw
```

Use `--json` when extracting ids, thread ids, Message-IDs, or structured address fields.

## Wait for inbound mail

```bash
heliox email wait --from github.com --subject verify --timeout 10m --json
heliox email wait --subject "Your verification code" --poll 3s --json
heliox email wait --since "2026-05-05T10:00:00Z" --limit 20 --json
```

Defaults:

- `--timeout 5m`
- `--poll 5s`
- `--since now`
- `--limit 20`

If no email matches before timeout, the command exits non-zero. Do not claim success.

## Send

```bash
heliox email send --to alice@example.com --subject "Hi" --body "Hello" --json
heliox email send --to "Alice <alice@example.com>" --to bob@example.com --cc carol@example.com --subject "Plan" --body-file ./body.txt --json
heliox email send --to a@b.com --subject "X" --body "plain text" --html-file ./body.html --json
```

Flags:

- `--to` is required and repeatable. Comma-separated addresses are accepted.
- `--cc` and `--bcc` are repeatable.
- `--subject` is required.
- Use either `--body` or `--body-file`, not both.
- `--html-file` adds optional HTML body.
- `--from-name` overrides the display name.

## Reply/threading

```bash
heliox email send --to support@vendor.com --subject "Re: ticket" --body "thanks" --in-reply-to "<msg-id@vendor.com>" --thread-id <thread_id> --json
```

`--in-reply-to` is the RFC 822 Message-ID of the parent message and must be owned by this AI user. `--thread-id` must refer to a thread containing at least one message owned by this AI user.
