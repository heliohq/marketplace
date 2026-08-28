---
name: email
description: "Use `heliox email ...` for everything involving the AI user's own email: reading or filtering the inbox (`--from`/`--subject`/`--since`), loading a full thread for context, reading a message body, waiting for an inbound mail (signup verification, OTP, vendor reply), sending new mail, or replying within a thread. Trigger whenever a task touches the assistant's inbox or outbound mail, even when the user never says the word 'email' (e.g. 'did the vendor get back to us', 'grab the code they sent me', 'let them know we're ready'). This is the only mail path; the runtime has no separate mail client."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox email --help"
---

# Heliox Email

Email commands operate as the authenticated AI user. There is no override flag for `ai_user_id`: the server reads it from the bearer claims on the runtime api-key.

The reads (`list`/`thread`/`read`/`wait`) act on the `id`, the `thread` id, and structured address fields. Pass `--json` to get them (that's your baseline `--json` rule; for these verbs you almost always need the fields). A `send` needs `--json` only when you'll use the sent message's ids afterward.

## The envelope-vs-body split (read this once, it governs every list)

`list` and `thread` return an **envelope** projection: `id`, `from`/`to`/`cc`, `subject`, `created_at`, `direction`, `thread`, and outbound `status`. **No message bodies.** You scan a page or a thread by envelope, then pull the one body you actually need with `email read <id>`. This is deliberate: one marketing email's HTML body can be tens of KB, so bodies never ride a multi-row surface.

`email read <email_id>` is the deep read: the envelope plus `body_text`, `bcc`, `reply_to`, and `attachment_ids`. You get `body_text`, and `body_html` rides alongside it whenever the sender provided an HTML part: the two MIME alternatives are not always equivalent (verification and password-reset links often live only in the HTML), so check both. A text-only email carries no `body_html`. `wait` returns its single matched message the same deep-read way (bodies included), so you act on it directly, no follow-up `read`.

## List and read

```bash
heliox email list --json
heliox email list --limit 10 --json
heliox email list --from alice --subject launch --since 2026-05-01T00:00:00Z --json
heliox email read <email_id> --json
```

`list` filters (all server-side, combine freely):

- `--from <substring>`: case-insensitive match on the From address. Special characters (`+`, `.`, `*`, …) match literally.
- `--subject <substring>`: case-insensitive match on the Subject.
- `--since <RFC3339>`: drops emails created before this timestamp; a malformed value fails fast with a non-zero exit, never silently widens the result set.
- `--limit N`: caps results (default 50, max 100). Filters apply first, then the cap.

## Inspect a thread

```bash
heliox email thread <thread_id> --json
```

Every email in the thread, oldest first, scoped to this AI user: envelope rows, no bodies (see the split above). Read a specific message's body with `email read <id>` using the `id` from a thread row. Reach for `thread` when the trigger entries in your session prompt don't carry enough history (e.g. the user is picking up a thread you opened weeks ago), or to confirm a thread's latest state before you compose a reply.

## Wait for inbound mail

```bash
heliox email wait --from github.com --subject verify --timeout 10m --json
heliox email wait --subject "Your verification code" --poll 3s --json
heliox email wait --since "2026-05-05T10:00:00Z" --json
```

Defaults: `--timeout 60s`, `--poll 5s`. Both accept Go duration syntax (`30s`, `2m`, `10m`). `--since <RFC3339>`, `--from`, and `--subject` use the same match rules as `list`, but each poll checks them client-side against only the 20 newest inbox emails, so a match older than those 20 never surfaces. Start the wait before you trigger the mail you expect; to find an email that may already be old, use `list` with server-side filters instead. If nothing matches before the timeout the command exits non-zero; do not claim success.

## Send

```bash
heliox email send --to alice@example.com --subject "Hi" --body "Hello" --json
heliox email send --to "alice@example.com,bob@example.com" --cc "carol@example.com" --subject "Plan" --body "Long body text..." --json
heliox email send --to alice@example.com --subject "Update" --body "..." --from-name "Wren" --json
```

- `--to` is required. Comma-separated for multiple recipients; the flag is **not** repeatable (`--to a --to b` keeps only the last).
- `--cc` / `--bcc` take the same comma-separated format.
- `--subject` is required.
- `--body` is required, plain-text only. No body-file/body-stdin workarounds. When the generated subject or body carries shell-sensitive characters (they routinely do), write the whole command's arguments as a JSON array to a file and run `heliox --args-file <path>`.
- `--from-name` overrides the display name on the From header.
- No attachments: `heliox email send` has no `-a`/attach flag (that's a message/task-send flag only). You can't attach bytes to an outbound email here; reference the material in the body text instead.

## Reply / threading

```bash
heliox email send --in-reply-to <email_id> --to <sender> --subject "Re: <original>" --body "thanks" --json
```

To reply, pass `--in-reply-to <email_id>`, the `id` of the message you're replying to (straight off a `list`/`read`/`thread` row). You never touch a raw RFC 822 Message-ID, and you do **not** pass the thread: the server resolves the parent, verifies you own it, threads the reply into the parent's thread, and stamps the `In-Reply-To` header for you.

A reply is still a full `send`, so you supply the envelope the CLI can't infer:

- `--to` is **not** derived from the parent. Set it to whoever you're answering: the parent's `from` address, or its `reply_to` when `email read` shows one.
- `--subject`: reuse the parent's subject, prefixed `Re: ` if it isn't already.

`--thread <thread_id>` is an optional override: pass it only to attach a send to a specific thread you own when there is no parent to reply to. Give both and the parent must belong to that thread.
