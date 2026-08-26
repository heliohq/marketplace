# Iterable (`heliox tool iterable -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Iterable is a
**flat provider** (not grouped like `google`): everything after `--` is the
iterable tool's own CLI. Iterable is a cross-channel marketing platform:
user (contact) profiles, custom events, subscription lists, campaigns, message
templates, and transactional email.

```bash
heliox tool iterable [--account <key>] -- <resource> <verb> [flags...]
```

## Connect (region matters: it is part of the key)

Iterable is an **api_key** tool: the user pastes one secret through the connect
link, no OAuth consent. Iterable runs **two isolated data centers** and every
project key is bound to exactly one, so the secret carries its region:

- `us:<key>` → US data center (`api.iterable.com`)
- `eu:<key>` → EU data center (`api.eu.iterable.com`)

A US key returns auth errors against the EU host and vice-versa, so the region
prefix is required; there is no auto-detect. To run **several projects in the
same data center** (e.g. staging + production, or one per brand) as separate
connections, add a project alias in the middle:

- `us:staging:<key>` → connection labelled "Iterable - US (staging)"
- `us:prod:<key>` → a distinct connection in the same data center

Without an alias there is **one connection per data center**: pasting a second
un-aliased US key **re-keys** the existing "Iterable - US" connection rather
than adding a second. Tell the user to add an alias when they want to keep
multiple same-region projects side by side. Use `--account <key>` (the label's
key, e.g. `us:staging`) to pick among connected accounts; a 409 lists them.

The key must be a **server-side** key (Iterable Settings → API Keys), not a
JWT-enabled one.

## Command surface

```bash
# Users (contacts)
heliox tool iterable -- user get --email a@b.com --json
heliox tool iterable -- user get --user-id 12345 --json          # by userId instead of email
heliox tool iterable -- user update --body '{"email":"a@b.com","dataFields":{"firstName":"Ada"}}' --json
heliox tool iterable -- user delete --email a@b.com --json
heliox tool iterable -- user fields --json                        # the project's user field schema

# Events
heliox tool iterable -- event track --body '{"email":"a@b.com","eventName":"signup"}' --json
heliox tool iterable -- event list --email a@b.com --limit 50 --json

# Lists (subscription lists)
heliox tool iterable -- list list --json
heliox tool iterable -- list subscribe   --body '{"listId":123,"subscribers":[{"email":"a@b.com"}]}' --json
heliox tool iterable -- list unsubscribe --body '{"listId":123,"subscribers":[{"email":"a@b.com"}]}' --json
heliox tool iterable -- list users --list-id 123 --json

# Campaigns & templates
heliox tool iterable -- campaign list --json
heliox tool iterable -- campaign metrics --campaign-id 456 --json
heliox tool iterable -- template list --json

# Transactional email (send an existing campaign/template to a user)
heliox tool iterable -- email send --body '{"campaignId":456,"recipientEmail":"a@b.com"}' --json

# Catalogs
heliox tool iterable -- catalog list --json
```

Write verbs take a raw `--body` JSON payload, passed through to Iterable
verbatim. Mirror the shapes in Iterable's API reference. `user update` needs
at least `email` or `userId`; `event track` needs `eventName` plus an
`email`/`userId`.

## Output & errors

Add `--json` for machine-readable output; responses are Iterable's JSON
verbatim. Iterable reports write results as `{"code":"Success", ...}`; the
tool treats any **non-Success code as a failure** (exit 1) even when HTTP is
200, so trust the exit code, not just the status. A bad or wrong-data-center
key surfaces as a `401`/credential-rejected on first use (there is no
connect-time verification). Exit 2 means a usage error (bad flags, malformed
`--body`, or a credential that is not `<region>:<key>` / `<region>:<alias>:<key>`).

## Safety

Sending transactional email (`email send`), subscribing/unsubscribing users,
and deleting a user are outward-facing, irreversible-ish actions against real
contacts. Follow the sensitive-operation rule in `../SKILL.md` and
confirm the recipient/list before firing.
