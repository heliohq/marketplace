# Webhook trigger authoring

A webhook trigger receives an external delivery and decides whether that
delivery deserves an AI run. Helio gives it a public URL; the URL is not a
secret and does not prove who sent the request.

## Research the provider contract

Use the provider's official webhook documentation to establish:

- event types and a representative raw payload;
- the exact signature algorithm and which bytes are signed;
- timestamp or replay-window requirements;
- the provider's stable delivery or event id;
- retry behavior and the success response it expects;
- how to configure the Helio URL on the source.

Prefer the provider's signed push even when the user says that checking every
few minutes would be acceptable only when you can finish provider registration
and prove delivery. The user described latency, not architecture. A connected
provider account does not itself register a webhook.

## Prove that registration is within reach

Before writing the handler, find the source's webhook management surface and
the permission needed to use it. Check whether your authorized provider tool,
API credential, or browser session can create and remove the subscription.

The acceptable paths are:

1. Register it yourself through an authorized API or browser, then save the
   provider's subscription identity in the build evidence for later cleanup.
2. For a custom system the user controls, provide the Helio URL and a small
   source-side request contract, then implement or configure that caller when
   you have access to it.
3. If neither is possible, keep the automation disabled and give the user one
   precise setup step in the source. Do not call it complete until that step
   and a source-originated test delivery are confirmed.

Do not replace registration proof with a `curl` to the public URL. That proves
the Helio ingress can receive a request; it does not prove the provider will
send the right event in production.

## Authenticate before interpreting

Start from `../templates/webhook-handler.mjs`. Verify the signature against the
raw request body before parsing or trusting fields. Use constant-time
comparison for MACs and enforce the provider's replay window when its signature
contains a timestamp.

Bind sensitive verification material through the trigger's single Vault
credential reference; do not copy it into `--env`. Public verification keys
and other non-sensitive configuration may use `--env`. If signature
verification and source enrichment require two independent credentials, the
current one-binding model cannot represent both safely. Simplify the handler
or explain the limitation instead of placing the second secret in code or
Lambda configuration.

Fetch the bound credential on every invocation, as the template does. Do not
cache plaintext across warm Lambda invocations: unbind, delete, rotate, and
delegation revocation must take effect on the next fetch. Treat a credential
endpoint `429` as a failed delivery and let the provider retry according to its
documented policy; never fall back to an earlier value.

If the provider cannot authenticate deliveries, do not use that webhook for an
automation with meaningful outward or irreversible effects. A guessed URL plus
rate limiting is not source authentication.

## Normalize, filter, identify, project

After verification:

1. Parse and validate the expected payload shape. Name every field the match,
   stable identity, and projected event require, including its type and whether
   an empty value is valid. Reject a missing or wrong-typed required field;
   never turn `undefined`, `null`, or an object into an apparent id with string
   coercion.
2. Normalize only the fields the predicate needs.
3. Apply an objective match and a source-shaped near miss.
4. Derive `fire_key` from the provider delivery id or a stable semantic event
   id. Fail closed if neither exists; never fall back to the API Gateway request
   id, invocation time, or a random UUID.
5. Project a minimal event for the executor. Do not forward signatures,
   secrets, authorization fields, or an unbounded raw payload.

Provider retries of the same delivery must produce the same key. Two distinct
provider events that happen at the same time must still produce different
keys.

Return success to the source only after Helio accepts the fire or confirms its
stable key was already handled. A Helio `429`, timeout, or `5xx` must fail the
webhook invocation so the source retries the same delivery. Never turn those
responses into a normal `{fired: false}` result: that acknowledges and loses an
event Helio did not accept.

## Required fixtures

Run local tests for:

- a valid signed event that should fire;
- a valid signed near miss that must stay quiet;
- an invalid signature;
- an expired replay timestamp where applicable;
- the same delivery id twice;
- a missing stable delivery id;
- a missing required business id and a wrong-typed predicate field;
- malformed JSON and an unsupported event type;
- proof that logs and the projected event contain no credential or signature.

After deployment, register the exact URL returned by `trigger create`. Send a
test from the provider's own delivery surface, confirm its delivery record,
inspect `trigger logs`, and then inspect the resulting Automation transcript.
Record enough provider-side identity to remove or repair the subscription
later. If registration remains manual, tell the user the automation is waiting
for that setup and leave it disabled.
