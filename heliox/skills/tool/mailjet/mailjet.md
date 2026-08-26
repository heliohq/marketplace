# Mailjet (`heliox tool mailjet -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Mailjet is a
**flat provider** (not grouped): everything after `--` is the mailjet tool's own
CLI. It sends transactional email (Send API v3.1) and manages contacts, lists,
templates, and stats over the Mailjet v3 REST API.

```bash
heliox tool mailjet [--account <key>] -- <group> <verb> [flags...]
```

## Connect

Mailjet uses an **API key pair**, not OAuth. The user creates a public **API
Key** and private **Secret Key** in Mailjet → Account Settings → API Key
Management (https://app.mailjet.com/account/apikeys) and pastes them joined by a
colon (`your-api-key:your-secret-key`) into the connect drawer. Helio verifies
the pair (a `GET /v3/REST/apikey` Basic-auth call) before storing it. Relay the
`heliox tool mailjet auth` link if nothing is connected; you cannot enter the
key yourself.

## Output shape

- REST **list** verbs return `{"data":[…],"count":N,"total":T}`. The provider's
  `{Count,Data,Total}` envelope is unwrapped; page with `--limit` / `--offset`.
- REST **get** verbs return the single record object.
- `send` returns the Send API v3.1 result verbatim: `Messages[]` with per-message
  `Status` and each recipient's `MessageID` / `MessageUUID`.

## Commands

### Send email (outward-facing: confirm before sending)

```bash
# --to is repeatable; each value is "email" or "Name <email>"
heliox tool mailjet -- send \
  --from-email you@yourdomain.com --from-name "You" \
  --to "Ada <ada@example.com>" --to bob@example.com \
  --subject "Hello" --text "Plain body" --html "<p>Rich body</p>" --json

# send a saved template with variables instead of inline body
heliox tool mailjet -- send --from-email you@yourdomain.com \
  --to ada@example.com --template-id 123456 \
  --variables-json '{"firstname":"Ada"}' --json
```

`--from-email` must be a validated Mailjet sender. Provide `--text`, `--html`, or
`--template-id`. `--cc` / `--bcc` are repeatable in the same `Name <email>` form.

### Contacts

```bash
heliox tool mailjet -- contact list --limit 20 --json
heliox tool mailjet -- contact get --id ada@example.com --json     # id or email
heliox tool mailjet -- contact create --email ada@example.com --name "Ada" --json
```

### Lists

```bash
heliox tool mailjet -- list list --json
heliox tool mailjet -- list create --name "Newsletter" --json
heliox tool mailjet -- list add-contact --contact-id 132 --list-id 77 --json
```

### Templates

```bash
heliox tool mailjet -- template list --json
heliox tool mailjet -- template get --id 555 --json     # editable content
```

### Messages (what was sent + delivery state)

```bash
heliox tool mailjet -- message list --campaign-id 42 --json
heliox tool mailjet -- message get --id 20547681647433000 --json
```

### Stats

```bash
# account/campaign/list delivery + open/click counters
heliox tool mailjet -- stat counters --counter-source Campaign --source-id 42 --json
# per-mailbox-provider deliverability for one campaign
heliox tool mailjet -- stat recipient-esp --campaign-id 42 --json
```

## Region

Mailjet processes data in the EU by default (`https://api.mailjet.com`). Accounts
moved to Mailjet's **US architecture** must add `--region us` (or
`--base-url https://api.us.mailjet.com`); the same key pair works against
whichever host the account lives on. Use it only if the default host returns
auth failures for a US-provisioned account.

## Errors

Exit `0` success, `1` API/runtime failure (with `--json`, an
`{"error":{"message","kind":"api","status"}}` envelope), `2` usage error. A
`401`/`403` means the key pair was rejected. Ask the user to reconnect with a
fresh key pair.
