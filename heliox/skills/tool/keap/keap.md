# Keap (`heliox tool keap -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Keap (formerly
Infusionsoft) is a small-business CRM + marketing-automation platform. It is a
**flat provider** (not grouped like `google`): everything after `--` is the
keap tool's own CLI, over the Keap REST **v2** API.

```bash
heliox tool keap [--account <key>] -- <resource> <verb> [flags...]
```

One connected account is one Keap tenant. The connection is a tenant-wide grant
(Keap's only OAuth scope is `full`), so a single connection can read and write
across the whole account — treat it with care.

## Command tree (resource → verb)

```
keap contact      list | get <id> | create | update <id> | delete <id>
keap company      list | get <id> | create | update <id>
keap tag          list | get <id> | create | contacts <id> | apply <id> | remove <id>
keap opportunity  list | get <id> | create | update <id> | stages
keap task         list | get <id> | create | update <id> | delete <id>
keap note         list | get | create | update | delete        (contact-scoped: --contact-id)
keap email        send | list
keap automation   list | get <id> | add-contacts <id>
keap campaign     list | get <id>                               (legacy Campaign Builder, read-only)
keap user         list | me
```

Every command prints the provider's JSON on stdout; add `--json` to force the
structured error envelope on failures.

## Listing and filtering

List verbs pass the v2 query params straight through:

```bash
heliox tool keap -- contact list --page-size 25 --filter "email==jo@x.com" --order-by given_name --fields id,given_name,email_addresses
heliox tool keap -- contact list --page-token <next_page_token>   # paginate with the token from the previous response
```

`--filter` / `--order-by` / `--fields` map 1:1 to Keap's v2 params; the
response's `next_page_token` is what you feed back into `--page-token`.

## Writing (convenience flags + `--json-body` escape hatch)

Create/update verbs expose flags for the common fields, plus `--json-body` for
the full v2 payload (custom fields, addresses, etc.). Keys in `--json-body`
overlay — and win over — the convenience flags:

```bash
# create a contact from common fields
heliox tool keap -- contact create --email jo@x.com --given-name Jo --family-name Ng --phone +15551234567

# create with custom fields via the escape hatch
heliox tool keap -- contact create --given-name Jo --json-body '{"custom_fields":[{"id":9,"content":"VIP"}]}'

# tag ops take repeatable --contact-id
heliox tool keap -- tag apply <tag-id> --contact-id 123 --contact-id 456
heliox tool keap -- tag remove <tag-id> --contact-id 123

# opportunities and tasks have required fields
heliox tool keap -- opportunity create --title "New deal" --contact-id 123 --stage-id <stage-id>
heliox tool keap -- task create --assigned-to-user-id <user-id> --title "Follow up" --contact-id 123
heliox tool keap -- opportunity stages          # list pipeline stages to get a --stage-id

# notes are contact-scoped; create requires the authoring user
heliox tool keap -- note create --contact-id 123 --user-id <user-id> --text "Called, left VM"

# drop contacts into an automation sequence
heliox tool keap -- automation add-contacts <automation-id> --sequence-id <seq-id> --contact-id 123
```

Use `keap user list` (or `keap user me`) to find the user id that `task create`
and `email send` require.

## Sending email

`keap email send` sends a one-off email to existing contacts — this **leaves the
user's account** and reaches real recipients, so it is a sensitive, outward-
facing action. Confirm intent before sending, per the sensitive-operation rule
in `../SKILL.md`.

```bash
heliox tool keap -- email send --contact 123 --contact 456 --subject "Hi" --user-id <user-id> --html "<p>Hello</p>"
```

## Notes / footguns

- **`--assigned-to-user-id` (tasks), `--user-id` (notes, email) are required by
  Keap**, not optional niceties — the create call 422s without them. Resolve a
  user id with `keap user me` / `keap user list` first.
- **`keap user me`** returns the authorizing user/tenant (`/v2/oauth/connect/userinfo`);
  the connection's account key is the Keap tenant, not the individual user.
- A `401 reconnect required` means the token was revoked or expired for good —
  relay a fresh `keap auth` link (see [../SKILL.md](../SKILL.md)); do not retry.
