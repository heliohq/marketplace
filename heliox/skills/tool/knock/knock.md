# Knock (`heliox tool knock -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Knock is a
**flat provider** (not grouped): everything after `--` is the knock tool's own
CLI.

```bash
heliox tool knock [--account <key>] -- <group> <verb> [flags...]
```

Knock is **notification infrastructure**. You model recipients, then trigger a
**workflow** that fans one event across whatever channels the workflow is
configured for (email, SMS, push, in-app, Slack…). You do not pick channels or
write templates from here. A human designs those in the Knock dashboard. Your
job is: send a notification to the right person, and check whether it landed.

## Connect

Knock uses an **environment-scoped secret API key** (`sk_...`), not OAuth. Ask
the user to connect it:

```bash
heliox tool knock auth --json      # relay the link; user pastes their sk_ key
```

Each Knock environment (Development, Production, custom) has its own key. The
key the user pastes decides which environment you act on. There is no flag to
switch environments. A bad or revoked key surfaces as a `401` on the first
call (reconnect to fix).

## The mental model (read this first)

- A **workflow** must already exist in the Knock environment (created by a
  human, addressed by its **key**). You trigger it; you do not create it.
- A **recipient** must be known to Knock before (or at) trigger time. Identify
  users first, or pass inline recipient objects. Triggering for an unknown bare
  id simply reaches nobody useful.
- **Delivery is asynchronous.** `workflow trigger` returns a `workflow_run_id`
  immediately; whether a message was delivered/seen/read is read afterward from
  the **message** endpoints.

## Core commands

### Send a notification (the #1 job)

```bash
# Trigger a workflow. --recipient is repeatable; --data is the JSON payload the
# workflow template renders.
heliox tool knock -- workflow trigger --key new-comment \
  --recipient user_123 --recipient user_456 \
  --data '{"comment":"Ship it","url":"https://..."}' --json

# ALWAYS dry-run first when unsure. --sandbox simulates the run without
# delivering anything: safe to confirm recipients/data before a real fan-out.
heliox tool knock -- workflow trigger --key new-comment \
  --recipient user_123 --sandbox --json

# Advanced: inline recipient objects (identify + notify in one call).
heliox tool knock -- workflow trigger --key welcome \
  --recipients-json '[{"id":"user_9","email":"a@b.co","name":"Ada"}]' --json

# Cancel queued runs you tagged with --cancellation-key at trigger time.
heliox tool knock -- workflow trigger --key digest --recipient user_1 --cancellation-key d-42 --json
heliox tool knock -- workflow cancel  --key digest --cancellation-key d-42 --json
```

`--idempotency-key <k>` makes a trigger safe to retry (24h dedup window). Use
it if you might resend the same notification.

### Know who to notify

```bash
heliox tool knock -- user identify --id user_123 --data '{"email":"a@b.co","name":"Ada","phone_number":"+1..."}' --json
heliox tool knock -- user get  --id user_123 --json
heliox tool knock -- user list --page-size 50 --json
heliox tool knock -- user merge --id user_keep --from-id user_dupe --json
```

Respect opt-outs and channel routing:

```bash
heliox tool knock -- user get-preferences --id user_123 --json
heliox tool knock -- user set-preferences --id user_123 --set default --data '{"channel_types":{"email":true}}' --json
heliox tool knock -- user set-channel-data --id user_123 --channel-id <ch> --data '{"tokens":["..."]}' --json
```

### Did it land? was it seen/read?

```bash
heliox tool knock -- message list --recipient user_123 --status delivered --json
heliox tool knock -- message get --id <message_id> --json
heliox tool knock -- message content --id <message_id> --json          # rendered content
heliox tool knock -- message events --id <message_id> --json           # lifecycle events
heliox tool knock -- message delivery-logs --id <message_id> --json    # provider send logs

# Update engagement (in-app feed). --undo clears it (except interacted).
heliox tool knock -- message mark --id <message_id> --state read --json
heliox tool knock -- message mark --id <message_id> --state seen --undo --json
```

### Non-user recipients, tenants, schedules

```bash
# Objects: a project/doc/account as a recipient, in a named collection.
heliox tool knock -- object set --collection projects --id proj_1 --data '{"name":"Apollo"}' --json
heliox tool knock -- object subscriptions --collection projects --id proj_1 --json

# Tenants: scope by customer/workspace for per-tenant branding.
heliox tool knock -- tenant set --id acme --data '{"name":"Acme"}' --json

# Schedules: send a workflow later or on a cadence.
heliox tool knock -- schedule create --recipient user_1 --workflow digest --scheduled-at 2026-08-01T09:00:00Z --json
heliox tool knock -- schedule delete --schedule-id sch_1 --json
```

## Output & errors

Every command prints Knock's JSON verbatim on stdout (lists are
`{entries, page_info}`; paginate with `--after <cursor>`). Empty-body
successes (cancel, some status marks) print `{"ok":true}`. Exit codes: `0` ok,
`2` for a bad flag / invalid `--data` JSON / missing required id, `1` for a
Knock API or transport error. A `401` means the key is invalid/revoked. Ask
the user to reconnect.

## Footguns

- **Trigger needs an explicit recipient**: the tool refuses an empty audience.
  This is deliberate; never guess a recipient.
- **`--sandbox` before a real send**: a workflow can fan out to many people
  across many channels. Dry-run first when the audience or data is uncertain.
- **The workflow key must exist** in the connected environment. A missing key
  returns a `404`, not a delivery.
- **`message list` needs a live message** to have been produced: a fresh
  environment with no sends returns empty `entries`.
