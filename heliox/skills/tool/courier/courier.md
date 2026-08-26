# Courier (`heliox tool courier -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Courier is a
**flat provider** (not grouped like `google`): everything after `--` is the
courier tool's own CLI.

```bash
heliox tool courier [--account <key>] -- <verb> [flags...]
```

Courier is **notification infrastructure**: you use it to **send a notification**
to a person, list, or audience across the workspace's configured channels
(email, SMS, push, Slack, …), then **track and manage** what you sent. The
load-bearing verb is `send`; everything else reads, tracks, or discovers who to
send to.

Connect is an **API key** (not OAuth): the user pastes a workspace API key from
Courier → Settings → API Keys. After that, the CLI injects it per call.

## The mental model (read this first)

`send` returns a `requestId` with a **202 "accepted"**: that means Courier took
the request, **not** that it was delivered. To know the outcome, look it up with
`message get <requestId>` (status) or `message history <requestId>` (the full
enqueued → sent → delivered / error timeline). The `requestId` of a
single-recipient send *is* its message id.

You send to **exactly one** recipient selector and **exactly one** content form:

- Recipient (pick one): `--user-id`, `--email`, `--phone`, `--list-id`, or
  `--audience-id`.
- Content (pick one): a `--template <id>` **or** an inline `--title` + `--body`
  pair (both required together).

Setting two recipients, or a template *and* an inline title, is a usage error
(exit 2): nothing is sent.

## Core commands

### Send

```bash
# inline content to one user
heliox tool courier -- send --user-id u_123 --title "Build done" --body "Your deploy finished." --json

# a saved template to an email, with template variables
heliox tool courier -- send --email person@example.com --template welcome --data '{"name":"Ada"}' --json

# to a whole list, pinning the channel with routing
heliox tool courier -- send --list-id monthly-digest --template digest \
  --routing '{"method":"single","channels":["email"]}' --json

# to an audience, branded
heliox tool courier -- send --audience-id aud_1 --template promo --brand-id brand_9 --json
```

`--data` / `--routing` are JSON objects; `--brand-id` picks a brand for
rendering. `send` prints `{"requestId":"..."}`.

### Track what you sent

```bash
heliox tool courier -- message get <requestId> --json              # delivery status
heliox tool courier -- message history <requestId> --json          # full delivery timeline
heliox tool courier -- message list --status DELIVERED --recipient u_123 --json
heliox tool courier -- message cancel <requestId> --json           # cancel an enqueued/delayed message
```

`message list` filters: `--status`, `--recipient`, `--notification`, `--list`,
`--tags` (comma-delimited), `--trace-id`, `--enqueued-after`. It paginates by
cursor only: pass `--cursor <c>` from the previous page's `paging.cursor`.

### Discover who to send to

```bash
heliox tool courier -- list list --json                            # mailing lists (items + paging)
heliox tool courier -- list get <list-id> --json
heliox tool courier -- list subscribe <list-id> <user-id> --json
heliox tool courier -- list unsubscribe <list-id> <user-id> --json

heliox tool courier -- audience list --json                        # audiences
heliox tool courier -- audience get <audience-id> --json

heliox tool courier -- profile get <user-id> --json                # a recipient's channels on file
heliox tool courier -- profile subscriptions <user-id> --json      # lists a user is on

heliox tool courier -- brand list --json                           # resolve a --brand-id
heliox tool courier -- brand get <brand-id> --json
```

### Automations

```bash
heliox tool courier -- automation invoke --automation '{"steps":[{"action":"send","template":"t1"}]}' \
  --recipient u_123 --data '{"k":"v"}' --json
```

`--automation` is a required JSON object (the ad-hoc automation definition);
`--recipient`, `--template`, `--brand`, `--data`, `--profile` are optional
top-level fields.

## Output and errors

Every command prints Courier's JSON on stdout verbatim. Exit codes: `0` success,
`1` API/runtime failure, `2` usage/parse error. With `--json`, an error is an
envelope `{"error":{"message":...,"kind":"usage|api","status":<HTTP>}}`; a `401`
means the key was rejected. Ask the user to reconnect.

## Footguns

- **202 is not "delivered."** Always confirm with `message get` /
  `message history` when the outcome matters.
- **One recipient, one content form.** Two recipient flags, or `--template` with
  `--title`, exits 2 before sending.
- **No `--limit`.** Courier paginates by cursor, not page size; loop on
  `--cursor` from `paging.cursor` until `paging.more` is false.
