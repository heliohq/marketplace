# Event trigger implementation

Read this reference only when an automation needs a webhook or poll trigger.
This is an engineering checklist for you, not a form for the user. Infer it by
reading the source documentation and a real sample. Ask the user only when a
remaining choice changes what they will experience, and ask it in plain
language.

Use the current official documentation for a public product and the
source-owner's API or event documentation for a private system. Record the URL,
title or version, retrieval time, and the exact facts the handler relies on in
the private build evidence. Then read one representative response or delivery
through the connected account. Documentation establishes the contract; the
sample establishes that this account can use it. Neither substitutes for the
other.

If authoritative documentation cannot be found, do not infer endpoint names,
payload fields, signatures, pagination, or retry behavior from convention. Ask
for one concrete documentation or access path in ordinary language and leave
the automation disabled. The executor does not re-research stable contracts on
every run; the refiner checks them again when observed behavior drifts or the
source starts failing.

The parent automation must be event-only: create it with neither `--cron` nor
`--start`. The server rejects attaching an event trigger to a schedule-backed
automation.

## Choose the arrival mechanism

Start with direction:

- **Pushed:** the source sends a delivery to Helio.
- **Observed:** Helio calls the source's read API on a cadence.

Do not infer direction from the word "API." A custom service that POSTs an
event to Helio is pushed and uses `--kind webhook`. A trigger that GETs a
provider API is observed and uses `--kind poll`. The CLI has no `api` kind.

Use a current managed provider path only when Helio can bind the requested
automation to it. A managed flow for one named template does not make that
provider a generic event source. Today Gmail's managed inbox wake belongs to
the Inbox Triage template. After the user agrees, install it:

```bash
heliox automation catalog install @helio/inbox-triage \
  --timezone <owner IANA timezone> \
  --idempotency-key <stable-approved-install-key> --json
```

Reuse the same key on any retry. The install stays disabled while its first
run executes; enable it only after that run finishes safely. A generic
`automation create` will not receive the managed wake; do not claim that any
arbitrary Gmail automation can subscribe to it.

Choose a generic webhook only when all of these are true:

1. The source can push an authenticated event with stable delivery identity.
2. You have an authorized API or browser path that can register Helio's URL in
   that source, or the user explicitly agrees to complete one concrete setup
   step there.
3. You can produce a source-originated test delivery and inspect the trigger
   logs and resulting Automation run.

A connected account proves API access, not webhook administration or event
subscription. Provider documentation that says webhooks exist proves only the
first condition. If registration cannot be completed, use a poll when the read
API can represent the user's event honestly. Otherwise keep the automation
disabled and describe the missing setup in plain language.

Use a poll when Helio must read the source and the API exposes enough
information to identify a new item, revision, or explicitly bucketed condition.

Do not ask the user which mechanism they want. "Within five minutes is fine"
describes acceptable delay. It does not turn a connection into a subscription,
and it does not excuse leaving provider registration unfinished.

- For a webhook, read [`webhook-triggers.md`](webhook-triggers.md) and start
  from `../templates/webhook-handler.mjs`.
- For a poll, read [`poll-triggers.md`](poll-triggers.md) and start from
  `../templates/poll-handler.mjs`.

## Write the trigger contract before code

Record these answers in your working notes. Do not show the contract or its
vocabulary to the user unless they ask how the automation works.

1. **Source:** the official event or API surface, authentication method, and
   one real representative response.
2. **Arrival:** managed provider, webhook, or poll, including direction and the
   evidence that the full registration path is available.
3. **Match:** an objective predicate that code can decide, plus a near miss
   from the right source that must stay quiet.
4. **Beginning:** whether the first observation ignores existing matches,
   processes them immediately, or replays a bounded recent period.
5. **Identity:** the stable source event id, resource id plus revision, or
   explicitly approved time bucket that identifies one logical fire.
6. **Repeat behavior:** once per event, once when a condition becomes true,
   or a deliberate reminder cadence while it remains true.
7. **Cardinality:** one fire per item or one bounded batch. Confirm that the
   expected volume fits the trigger's rate and payload limits.
8. **Payload:** only the facts and links the executor needs, with no
   credential material and at most 64 KB of JSON.
9. **Failure:** what timeout, pagination limit, rate limit, malformed data,
   or authentication failure looks like. An unreadable source is not a quiet
   source.

Natural phrasing often resolves the beginning without a question. "From now
on" and "when a new one arrives" mean future-only. "Tell me if anything is
already wrong" includes current matches. If neither reading is safe to infer,
ask: "Should I include things that are already there, or only new ones from
now on?"

Do not build until the contract has a stable identity. Invocation time,
`Date.now()`, a Lambda request id, and a random UUID identify the check, not the
external event, so retries would wake the AI twice.

## Handler and deployment contract

The trigger is a small Node.js Lambda packaged as a zip whose root contains
`handler.mjs` exporting `handler`. Build dependencies into the zip; Helio
deploys the artifact but does not run `npm install`.

```bash
heliox automation trigger create --automation <id> --kind webhook --name <name> --code <file.zip>
heliox automation trigger create --automation <id> --kind poll --name <name> --cron "*/5 * * * ? *" --code <file.zip>
```

Create currently returns a one-time plaintext fire token with the trigger
result. The Lambda already receives it as `HELIO_AUTOMATION_FIRE_TOKEN`; it is
not a value to configure at the provider. Treat it as sensitive tool output:
never quote it, copy it into a file, pass it through `--env`, include it in
registration instructions, log it, or show it to the user.

These are the only generic event trigger kinds. When a user controls a custom
system and wants "an API to call," return the webhook URL and teach that caller
the accepted event shape. Do not invent `--kind api`.

Use `--env` only for non-sensitive configuration. When the handler needs one
credential already granted to the automation's executor, bind its Vault id:

```bash
heliox automation trigger create ... --credential <vault-credential-id>
heliox automation trigger update <trigger-id> --credential <vault-credential-id>
heliox automation trigger update <trigger-id> --clear-credential
```

The id is a reference, not a secret. Helio checks the executor's current Vault
owner or trust access before saving it. The Lambda can fetch only the one
server-side binding; it cannot choose another credential or list grants. Fetch
it on every invocation so lifecycle changes take effect immediately. Never
cache it or print the token, Authorization header, response body, or decoded
credential. A one-time delegation cannot back a recurring trigger.

When the handler decides to fire, it posts to
`HELIO_AUTOMATION_FIRE_URL` using `HELIO_AUTOMATION_FIRE_TOKEN` and:

```json
{"fire_key": "<stable logical event identity>", "event": {}}
```

The execution uniqueness boundary is `(automation_id, fire_key)`. Overlapping
poll windows and webhook retries are safe only when they derive the same key
for the same logical event.

## Prove both halves

There is no platform dry-run mode: a deployed fire is real. Exercise the
handler locally with source-shaped fixtures before deployment:

- a representative match that should fire;
- a near miss that must stay quiet;
- the same logical event delivered twice;
- malformed data and an upstream failure;
- invalid signature or poll boundary cases from the relevant reference.

Keep effects pointed at the owner or a scratch destination. Finish these local
checks and the manual procedure rehearsal while the event-only parent remains
disabled. After the handler is deployed and source registration is ready,
enable the parent for the contained source-originated proof:

```bash
heliox automation update <automation-id> --enable true
```

This enable is required for the proof: both credential fetch and fire reject a
disabled parent automation. Inspect trigger logs separately from the automation
run transcript:

```bash
heliox automation trigger logs <id> --last 20
heliox automation run show <execution_id> --transcript --json
```

For a webhook, keep three proofs separate: the provider shows the registration,
the provider's own test delivery appears in trigger logs, and the resulting run
transcript shows that the AI understood the event. For a poll, prove a real
scheduled Lambda invocation, the source read and filter decision, and the run.
None of these substitutes for another.

If a required proof fails, the audience is incomplete, the user asked to wait,
or a high-risk choice remains unresolved, disable the parent immediately with
`heliox automation update <automation-id> --enable false`. When every required
path holds and the user already authorized ongoing operation, leave it enabled;
otherwise restore it to disabled after the proof.

Fix code in place:

```bash
heliox automation trigger update <id> --code <file.zip>
```

An in-place update preserves the webhook URL and fire token. Recreating the
trigger breaks external systems configured with the old URL.
