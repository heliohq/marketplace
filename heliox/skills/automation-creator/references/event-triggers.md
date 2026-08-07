# Event trigger implementation

Read this reference only when an automation needs a poll or webhook trigger.

The parent automation must be EVENT-ONLY: created with neither `--cron` nor
`--start`. The three trigger kinds are mutually exclusive, and the server
rejects attaching an event trigger to a schedule-backed automation.

## Pick webhook or poll

Prefer `webhook` when the source can push a signed, stable event. It is fresher
and avoids repeated checks. Use `poll` when the source has no reliable push
surface or the user explicitly needs periodic observation.

- A poll trigger lets a small Lambda check frequently and fire the AI only
  when something deserves attention. This avoids starting a full AI run just
  to discover that nothing changed.
- A webhook trigger exposes `webhook.helio.im/<trigger_id>` in production.
  In test, configure the exact URL returned by `trigger create`; Helio does not
  configure the external system.

## Handler contract

The trigger is a small Node.js Lambda packaged as a zip whose root contains
`handler.mjs` exporting `handler`. Build dependencies into the zip; Helio
deploys the artifact but does not run `npm install` for it.

```bash
heliox automation trigger create --automation <id> --kind webhook --name <name> --code <file.zip> [--env K=V ...]
heliox automation trigger create --automation <id> --kind poll --name <name> --cron "*/5 * * * ? *" --code <file.zip>
```

Start webhook work from `../templates/webhook-handler.mjs`.

When the handler decides to fire, POST to
`process.env.HELIO_AUTOMATION_FIRE_URL` with:

```text
Authorization: Bearer ${process.env.HELIO_AUTOMATION_FIRE_TOKEN}
```

and JSON:

```json
{"fire_key": "<stable source delivery id>", "event": {}}
```

The platform injects `HELIO_AUTOMATION_FIRE_URL`,
`HELIO_AUTOMATION_FIRE_TOKEN`, and `HELIO_AUTOMATION_TRIGGER_ID`. Prefer the
source's delivery id for `fire_key`; it is the idempotency boundary for
retries.

## Authenticate webhooks

The public webhook URL is not a secret. Verify the source before firing:

- For GitHub, Stripe, and other HMAC-signing sources, verify the signature
  header against a shared secret supplied through `--env`.
- If a source cannot sign, the URL plus rate limiting is weaker protection.
  Avoid this for workflows with meaningful side effects.

Verification is required when the automation sends mail, changes data, spends
money, or otherwise has a significant blast radius. The platform stores and
runs the handler; it does not validate the source payload for you.

## Evaluate trigger code locally

There is no platform dry-run mode: a deployed fire is a real fire. Exercise
the handler locally with the cases justified by the workflow. Common useful
fixtures are:

- representative event that should fire;
- irrelevant or no-change event that should not fire;
- invalid signature;
- duplicate delivery id;
- malformed payload or upstream failure.

Keep side effects intercepted or sandboxed. After deployment, inspect trigger
logs separately from the automation run transcript:

```bash
heliox automation trigger logs <id> [--last 20]
heliox automation run show <execution_id> --transcript
```

Trigger logs prove event recognition and firing. The run transcript proves
that the AI understood the procedure and delivered correctly. Neither is a
substitute for the other.

## Update in place

Fix deployed code without recreating the trigger:

```bash
heliox automation trigger update <id> --code <file.zip>
```

An in-place update preserves the webhook URL and fire token. Deleting and
recreating the trigger breaks external systems configured with the old URL.
