# Loops (`heliox tool loops -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Loops is a
**flat provider** (not grouped like `google`): everything after `--` is the
loops tool's own CLI. It authenticates with the user's Loops **team API key**
(entered once at connect; injected automatically per call).

```bash
heliox tool loops [--account <team>] -- <group> <verb> [flags...]
```

Loops is a transactional-email + audience platform. This tool wraps the CRM +
messaging core you actually drive from chat — contacts, custom properties,
events (which trigger Loops workflows), transactional email, and mailing lists.
The heavy campaign/workflow *authoring* surface is intentionally not exposed;
that is human configuration in the Loops UI. Every command prints the
provider's JSON response verbatim on stdout.

## Verify the connection

```bash
heliox tool loops -- whoami --json     # → {success, teamName}; also the connect identity
```

## Contacts

A contact is keyed by `email` and/or an external `userId`.

```bash
# create (email required); first-class fields are named flags
heliox tool loops -- contact create --email a@e.com \
  --first-name Ada --last-name Lovelace --user-group beta --subscribed=true

# custom properties: repeatable --property key=value (typed-coerced:
# true/false→bool, numeric→number, else string). Custom props must already
# exist in Loops (see contact-property create). --properties-json '<obj>' is an
# escape hatch merged into the body.
heliox tool loops -- contact create --email a@e.com --property plan=pro --property seats=5

# update / upsert — needs email OR userId (both allowed, e.g. attach a userId)
heliox tool loops -- contact update --user-id u1 --first-name Grace

# find / delete / suppression — exactly ONE of --email / --user-id
heliox tool loops -- contact find --email a@e.com --json
heliox tool loops -- contact delete --user-id u1
heliox tool loops -- contact suppression get --email a@e.com --json
heliox tool loops -- contact suppression remove --email a@e.com
```

`--mailing-list <id>=true|false` (repeatable) subscribes/unsubscribes the
contact on a list; get the ids from `list ls`.

## Custom contact properties

Properties must exist before a contact can carry them.

```bash
heliox tool loops -- contact-property list --list custom --json
heliox tool loops -- contact-property create --name planName --type string   # type: string|number|boolean|date
```

## Events (trigger workflows)

Firing an event triggers any Loops workflow listening for it.

```bash
heliox tool loops -- event send --event-name signup --email a@e.com \
  --event-property plan=Pro --event-property count=3
```

`--event-name` is required plus one of `--email` / `--user-id`. Optional
`--event-properties-json '<obj>'`, `--mailing-list id=bool`, and
`--idempotency-key <key>` (409 on replay).

## Transactional email

Send a templated transactional email by its Loops template id.

```bash
# list templates (and their data-variable names); deprecated by Loops but functional
heliox tool loops -- email list --json

# send — email + transactional-id required; data variables fill the template
heliox tool loops -- email send --email a@e.com --transactional-id tmpl_123 \
  --data-variable name=Chris --data-variable resetLink=https://example.com/r
```

Optional: `--data-variables-json '<obj>'`, `--add-to-audience` (create the
contact if absent), `--attachments-json '<array>'` (must be enabled by Loops
support), `--idempotency-key <key>`.

## Mailing lists

```bash
heliox tool loops -- list ls --json     # ids feed --mailing-list on contact/event
```

## Footguns

- **Exactly one identifier** for `contact find`/`delete`/`suppression`: pass
  `--email` OR `--user-id`, never both (the tool rejects both client-side; the
  live API 400s on both anyway). `contact update` and `event send` allow both
  but need at least one.
- **Custom properties must pre-exist.** Setting `--property foo=bar` on a
  contact fails unless `foo` was created via `contact-property create`.
- **`subscribed` is only sent when you pass `--subscribed`.** Omit it on updates
  unless you specifically intend to (un)subscribe — Loops leaves it untouched.

## Exit codes

`0` success · `1` runtime/API failure (a `401` also drops the stored key so the
user is prompted to reconnect) · `2` usage/parameter error. Add `--json` to get
errors as a structured `{"error":{message,kind,status}}` envelope on stderr.
