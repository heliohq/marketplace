# Brevo (`heliox tool brevo -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Brevo
(formerly Sendinblue) is a **flat provider** (not grouped like `google`):
everything after `--` is the brevo tool's own CLI. Brevo covers email
marketing, transactional email, a contact database, and a light CRM.

```bash
heliox tool brevo [--account <key>] -- <resource> <verb> [flags...]
```

Output is the provider's JSON, passed through verbatim. Add `--json` to any
command to get errors as a structured envelope
(`{"error":{"code","message","status"}}`) carrying Brevo's own error code.

## The #1 footgun: verify the sender before sending

**Brevo blocks every email-send API call from an unverified sender**, even for
testing. Before `email send` or `campaign create`, list the account's verified
senders and pick one, or the send returns a 400.

```bash
heliox tool brevo -- sender ls --json           # verified senders (email + id)
heliox tool brevo -- account get --json         # account identity, plan, credits
```

`email send` (a one-off transactional/event email) and `campaign create` (a
scheduled bulk marketing campaign) are **distinct** Brevo surfaces. Don't use
one for the other.

## Send a transactional email

```bash
# minimal: recipient + verified sender + subject + body
heliox tool brevo -- email send \
  --to jane@acme.com --sender-email noreply@myco.com --sender-name "MyCo" \
  --subject "Your summary" --html "<p>Hello</p>"

# multiple recipients, cc/bcc, reply-to
heliox tool brevo -- email send --to a@x.com --to b@x.com \
  --cc boss@x.com --bcc audit@x.com --reply-to support@myco.com \
  --sender-id 3 --subject "Update" --html "<p>Hi</p>"

# use a Brevo template + params instead of inline html
heliox tool brevo -- email send --to jane@acme.com --sender-id 3 \
  --template-id 7 --params-json '{"NAME":"Jane"}'
```

`--sender-id` (a verified sender id from `sender ls`) takes precedence over
`--sender-email`/`--sender-name`. For full control of recipients, pass
`--to-json '[{"email":"x","name":"Y"}]'` (overrides `--to`).

## Manage contacts

```bash
# add / upsert (use --update-enabled to update if the contact already exists)
heliox tool brevo -- contact create --email jane@acme.com --update-enabled \
  --list-ids 3 --list-ids 5 --attributes-json '{"FIRSTNAME":"Jane"}'

heliox tool brevo -- contact get --id jane@acme.com --json
heliox tool brevo -- contact list --limit 50 --offset 0 --json
heliox tool brevo -- contact update --id jane@acme.com --attributes-json '{"SMS":"+123"}'
heliox tool brevo -- contact delete --id jane@acme.com
```

`--id` accepts an email, contact id, or ext_id; add `--identifier-type
contact_id|email_id|ext_id` when the value is ambiguous. Attribute names are
**uppercase** (`FIRSTNAME`, not `firstname`). List ids are **integers**.

## Lists and campaigns

```bash
heliox tool brevo -- list ls --json                        # discover list ids
heliox tool brevo -- list create --name "Newsletter" --folder-id 1
heliox tool brevo -- list add-contacts --id 5 --emails a@x.com --emails b@x.com

heliox tool brevo -- campaign list --type classic --status sent --json
heliox tool brevo -- campaign get --id 42 --json
heliox tool brevo -- campaign create --name "Promo" --subject "Sale" \
  --html "<p>Buy</p>" --sender-id 3 --list-ids 5 --scheduled-at 2030-01-01T10:00:00Z
```

Omit `--scheduled-at` on `campaign create` to leave the campaign as a draft.

## Footguns

- **Unverified sender → 400.** Always `sender ls` first (see above).
- **List ids are integers**, not names: resolve them with `list ls`.
- **`contact create` without `--update-enabled` fails on an existing contact**
  (Brevo force-merges only when upsert is enabled).
- **Transactional vs campaign** are different endpoints: `email send` is a
  one-off, `campaign create` is a scheduled bulk send.
- A bad API key surfaces as `401 unauthorized`; ask the user to reconnect.
