# Resend (`heliox tool resend -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Resend is a
**flat provider**: everything after `--` is the Resend tool's own CLI, speaking
the Resend REST API with the connected account's API key. Output is the
provider's JSON, verbatim.

```bash
heliox tool resend [--account <key>] -- <resource> <verb> [flags...]
```

Resources: `email` (the reason this tool exists), `domain`, `audience`,
`contact`, `broadcast`. Run `-- <resource> <verb> --help` for the full flag
surface.

## Sending email (the primary job)

```bash
heliox tool resend -- email send \
  --from "Onboarding <onboarding@yourdomain.com>" \
  --to user@example.com --subject "Welcome" --text "Hi there"
```

- **`--from` must be an address on a VERIFIED sending domain.** This is the #1
  failure: a send from an unverified domain returns `403 validation_error`
  ("the domain is not verified"); that is a plain API error to act on (verify
  the domain / pick a valid `from`), **not** a bad key. Check what you can send
  from first with `domain list`.
- Provide `--html` and/or `--text`. `--to` is repeatable, max 50 recipients;
  `--cc`, `--bcc`, `--reply-to` are also accepted.
- **`--idempotency-key <key>`**: pass a unique key per logical send so a
  retried send never double-delivers (24h dedup window). Use it whenever a send
  might be retried.
- **`--scheduled-at`** takes ISO-8601 (`2026-08-01T09:00:00Z`) or natural
  language (`"in 1 min"`, `"tomorrow 9am"`). Reschedule with
  `email update <id> --scheduled-at ...`, cancel with `email cancel <id>`.
- Structured fields are raw-JSON flags: `--attachments '[{"filename":"r.pdf",
  "content":"<base64>"}]'`, `--tags '[{"name":"env","value":"prod"}]'`,
  `--headers '{"X-Entity-Ref-ID":"abc"}'`.

Check delivery status later with `email get <id>`.

## Bulk send

```bash
heliox tool resend -- email batch --emails '[{...}, {...}]'   # up to 100
```

**Footgun: `email batch` does NOT support attachments**. The batch endpoint
rejects them. `scheduled_at` and `tags` per email are fine. For any email with
an attachment, use single `email send`.

## Marketing lists (secondary)

Audiences hold contacts; broadcasts send to an audience.

```bash
heliox tool resend -- audience create --name "Newsletter"
heliox tool resend -- contact create --audience <aid> --email a@b.com --first-name Ada
heliox tool resend -- broadcast create --audience <aid> --from "News <news@yourdomain.com>" \
  --subject "March update" --html "<p>...</p>"
heliox tool resend -- broadcast send <broadcast-id> [--scheduled-at "tomorrow 9am"]
```

Contacts are addressed by id **or** email under their audience
(`contact get|update|delete <id-or-email> --audience <aid>`).

## Domains

`domain list` / `domain get <id>` tell you which sending domains exist and
their verification state: read these before choosing a `from`. Provisioning
verbs (`domain create --name ... [--region ...]`, `domain verify <id>`,
`domain update`, `domain delete`) exist but are low-frequency account setup;
DNS still has to be configured in the user's registrar for `verify` to pass.

## Safety

Sending email and broadcasts are **outward-facing actions** on the user's real
Resend account and reach real inboxes: follow the sensitive-operation rule from
`../SKILL.md`; confirm recipients and content with the user before the
first send of a session, and never send anything the user has not sanctioned.
Use `--idempotency-key` on retriable sends so a re-run cannot double-deliver.
