# beehiiv (`heliox tool beehiiv -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. beehiiv is a
**flat provider** (not grouped like `google`): everything after `--` is the
beehiiv tool's own CLI, hitting the beehiiv v2 REST API. Every command prints
the provider's JSON envelope verbatim.

```bash
heliox tool beehiiv [--account <key>] -- <resource> <verb> [flags...]
```

## The mental model (read this first: it prevents the #1 footgun)

**Almost everything is publication-scoped.** A beehiiv workspace can hold
several publications, and posts / subscribers / segments / tiers all live under
one publication. So the flow is always:

1. `publication list` → pick the `pub_…` id you want.
2. Pass that id as `--publication-id pub_…` to every other command.

`--publication-id` is **required** on every command except `publication list`.
A value that does not start with `pub_` is rejected before any request is made.

## Core commands

### Discover

```bash
# publications this connection can see (start here to get the pub_… id)
heliox tool beehiiv -- publication list --json
heliox tool beehiiv -- publication get pub_00000000-0000-0000-0000-000000000000 --json

# reference data you need before writing subscribers (valid tiers / custom-field names)
heliox tool beehiiv -- tier         list --publication-id pub_… --json
heliox tool beehiiv -- custom-field list --publication-id pub_… --json
heliox tool beehiiv -- segment      list --publication-id pub_… --json
heliox tool beehiiv -- automation   list --publication-id pub_… --json
```

### Report on the newsletter (posts are read-only)

```bash
# list posts with stats; filters and expand are optional
heliox tool beehiiv -- post list --publication-id pub_… \
  --expand stats --status confirmed --order-by publish_date --direction desc --limit 25 --json

# one post's performance (--expand repeatable)
heliox tool beehiiv -- post get post_… --publication-id pub_… --expand stats --json
```

The tool does **not** create or send posts: authoring/sending is an app-only
flow, so `post` is read-only here.

### Subscribers (the primary write path)

```bash
# look a subscriber up by email (email is URL-encoded for you)
heliox tool beehiiv -- subscription get-by-email person@example.com \
  --publication-id pub_… --expand stats --expand custom_fields --json

# list / filter subscribers
heliox tool beehiiv -- subscription list --publication-id pub_… \
  --status active --tier premium --limit 50 --json

# add a subscriber: --email is required; --data carries any optional fields as a JSON object
heliox tool beehiiv -- subscription create --publication-id pub_… \
  --email new@example.com \
  --data '{"reactivate_existing":true,"send_welcome_email":true,"utm_source":"helio","custom_fields":[{"name":"Plan","value":"pro"}]}' --json

# update a subscriber (PUT): --data is the JSON object of fields to change
heliox tool beehiiv -- subscription update sub_… --publication-id pub_… \
  --data '{"tier":"premium"}' --json
heliox tool beehiiv -- subscription update sub_… --publication-id pub_… \
  --data '{"unsubscribe":true}' --json
```

Run `-- <resource> --help` (or `-- <resource> <verb> --help`) for exact flags
rather than guessing.

## Footguns (where agents go wrong)

- **`--publication-id` is required everywhere except `publication list`.** Run
  `publication list` first; passing a non-`pub_` value is a usage error (exit
  2), not a silent 404.
- **`subscription create` needs `--email`; everything else rides `--data`.**
  `--data` is a JSON **object** (validated before the call). The `--email` flag
  always wins over any `email` inside `--data`.
- **Update is a full-field JSON object, and it is a `PUT`.** Send only the
  fields you want to change: `{"tier":"premium"}`, `{"unsubscribe":true}`,
  `{"email":"new@addr"}`, `{"custom_fields":[{"name":"Plan","value":"pro","delete":false}]}`.
- **Reference names/ids before writing.** `tier`/`custom-field`/`automation`
  `list` give the valid values `subscription create`/`update` reference: a
  wrong tier or custom-field name is rejected by the API.
- **`--expand` is repeatable** (`--expand stats --expand custom_fields`), and
  only some values are valid per resource (posts vs subscriptions differ).
  Check `--help`.
- **`--account` when more than one beehiiv account is connected.** A `409`
  lists the candidate account keys; re-run with `--account <key>` before `--`.

## Safety

- Adding, re-activating, or unsubscribing a reader, and sending a welcome
  email, are outward-facing actions against the user's audience. Follow the
  sensitive-operation rule in [../SKILL.md](../SKILL.md) and confirm scope
  (especially bulk changes or `send_welcome_email`) before running one.
- Never echo tokens or credential payloads; the CLI never shows them to you.
