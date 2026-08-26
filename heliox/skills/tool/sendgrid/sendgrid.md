# SendGrid (`heliox tool sendgrid`)

Read `../SKILL.md` first for the connect/use model. SendGrid is a **flat**
provider connected with an **API key** (not OAuth): the user pastes a key,
Helio verifies and stores it, and every call injects it as a Bearer token.
Everything after `--` goes to the tool.

```bash
heliox tool sendgrid -- <args...>
heliox tool sendgrid --account <key> -- <args...>   # only if >1 key connected
```

`--region eu` (or `SENDGRID_REGION=eu`) targets the EU data-residency host; the
default is the global host. Use it only if the connected key belongs to an EU
subuser.

## Command surface

| Command | Does |
| --- | --- |
| `scopes` | Verify the key and list its granted scopes |
| `sender list` | Verified sender identities: the valid `from` addresses |
| `mail send` | Send an email (raw content or a dynamic template) |
| `template list` / `template get --id <id>` | Dynamic templates and their versions |
| `contact upsert` / `contact search --email <e>` | Add/update and look up marketing contacts |
| `list ls` | Marketing lists |
| `suppression bounces` / `unsubscribes` / `blocks` | Deliverability suppression lists |
| `stats --start-date YYYY-MM-DD` | Aggregated sending stats |

`--help` after `--` is the full reference for any command.

## Sending mail: the three things that bite

1. **`from` must be a verified sender.** A send from an unverified address fails
   with a 403 ("does not match a verified Sender Identity"): that is NOT a bad
   key, it is an account-setup gap. Run `sender list` first and use one of those
   addresses; if none exist, the user must verify a sender in the SendGrid UI.

   ```bash
   heliox tool sendgrid -- mail send \
     --to rcpt@example.com --from you@verified.com \
     --subject "Hello" --text "Plain body" --html "<p>Rich body</p>"
   ```

2. **Templated sends** use `--template-id` + `--data` (the
   `dynamic_template_data` JSON); omit `--subject`/`--text`/`--html` when the
   template supplies them. Get ids from `template list`.

   ```bash
   heliox tool sendgrid -- mail send \
     --to rcpt@example.com --from you@verified.com \
     --template-id d-abc123 --data '{"first_name":"Ada"}'
   ```

   For anything the flags don't cover (multiple personalizations, attachments,
   categories, `send_at`, ASM), pass a full v3 body with `--json-body '<json>'`.

3. **"Accepted" is not "delivered."** A successful send returns
   `{"status":"accepted","message_id":"..."}`. That means SendGrid queued it,
   not that it reached the inbox. Report it as *accepted / queued*, never as
   *delivered*. The `message_id` is the tracking id for later lookup.

## Contacts are asynchronous

`contact upsert` returns a `job_id` and queues the contact: it is **not stored
immediately**. Do not claim the contact was created. Confirm with
`contact search --email <e>` (it may take a moment to appear).

```bash
heliox tool sendgrid -- contact upsert --email lead@example.com --first-name Ada
heliox tool sendgrid -- contact search --email lead@example.com
```

## Errors

Beyond the shared table in `../SKILL.md`:

- **403** on a command is usually a scope gap (the key lacks permission for that
  operation) or an unverified `from`, not a dead key. Reconnecting won't help;
  the user needs a key with the right scope, or a verified sender.
- **401** means the key is invalid/revoked: ask the user to reconnect with a
  fresh key.

## Safety

Sending mail is an outward-facing action. Follow the sensitive-operation rule
in `../SKILL.md`: confirm the recipient list, subject, and body with the
user before sending anything that leaves their account.
