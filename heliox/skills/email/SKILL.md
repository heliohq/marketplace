---
name: email
description: "Use `heliox email ...` for the AI user's email inbox and outbound mail: listing or filtering recent emails (--from / --subject / --since), inspecting a full thread, waiting for verification emails, reading a message, sending new mail, replying within a thread, or handling email-based auth and vendor flows. Trigger whenever the assistant needs to read its own inbox, fetch a full email thread for context, wait for an inbound mail (signup verification, OTP, vendor reply), send mail to a third party, or reply within an existing email thread — this is the only path; the runtime has no separate mail client."
user-invocable: false
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox email --help"
---

# Heliox Email

Start by reading `../shared/SKILL.md`.

Email commands operate as the authenticated AI user. There is no override flag for `ai_user_id` — the server reads it from the bearer claims on the runtime api-key. `HELIO_EMAIL_BASE_URL` must be set in the runtime env for email commands to dial the email-service surface.

## List and read

```bash
heliox email list --json
heliox email list --limit 10 --json
heliox email list --from alice --subject launch --since 2026-05-01T00:00:00Z --json
heliox email read <email_id> --json
```

`email read` returns the full message body (text + html if present). There is no `--format` flag — the JSON body carries both parts and the caller picks.

Use `--json` when extracting ids, thread ids, Message-IDs, or structured address fields.

`list` filters (all server-side; combine freely):

- `--from <substring>` — case-insensitive match on the From address. Special characters (`+`, `.`, `*`, …) match literally.
- `--subject <substring>` — case-insensitive match on the Subject.
- `--since <RFC3339>` — drops emails created before this timestamp; a malformed value fails fast with exit code, never silently widens the result set.
- `--limit N` — caps results (default 50, max 100). Filters are applied first, then the cap.

## Inspect a thread

```bash
heliox email thread <thread_id> --json
```

Returns every email in the thread (oldest first), scoped to this AI user. `--json` includes full `body_text` (and `body_html` if present) for each message; the default table view shows envelope columns only (id, created_at, direction, from, subject).

Use when:

- You're in an email entity-session and the trigger entries above don't carry enough conversation history (e.g., the user is replying to a thread you opened weeks ago).
- You want to confirm the latest state of a thread before composing a reply.

`thread --json` is the one-shot way to load the full conversation; you only need `heliox email read <email_id> --json` when you have an isolated `email_id` and no thread context.

## Wait for inbound mail

```bash
heliox email wait --from github.com --subject verify --timeout 10m --json
heliox email wait --subject "Your verification code" --poll 3s --json
heliox email wait --since "2026-05-05T10:00:00Z" --json
```

Defaults:

- `--timeout 60s`
- `--poll 5s`

Both are string flags accepting Go duration syntax (`30s`, `2m`, `10m`). `--since <RFC3339>` filters out emails created before that timestamp; `--from <substring>` and `--subject <substring>` are case-insensitive substring matches.

If no email matches before the timeout, the command exits non-zero. Do not claim success.

## Send

```bash
heliox email send --to alice@example.com --subject "Hi" --body "Hello" --json
heliox email send --to "alice@example.com,bob@example.com" --cc "carol@example.com" --subject "Plan" --body "Long body text..." --json
heliox email send --to alice@example.com --subject "Update" --body "..." --from-name "Wren" --json
```

Flags:

- `--to` is required. Comma-separated addresses for multiple recipients; the flag itself is **not** repeatable (`--to a --to b` only keeps the last value).
- `--cc` and `--bcc` accept the same comma-separated format.
- `--subject` is required.
- `--body` is required — plain-text only. Do not use body-file/body-stdin workarounds. For generated email text, pass the body as one argv element with the shared `subprocess.run([...], shell=False)` pattern.
- `--from-name` overrides the display name on the From header.

## Reply / threading

```bash
heliox email send --to support@vendor.com --subject "Re: ticket" --body "thanks" --in-reply-to "<msg-id@vendor.com>" --thread <thread_id> --json
```

- `--in-reply-to` is the RFC 822 Message-ID of the parent message; must be owned by this AI user.
- `--thread` is the thread id to attach to (NOT `--thread-id`). Must refer to a thread containing at least one message owned by this AI user.
