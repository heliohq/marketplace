# Poll trigger authoring

A poll trigger runs cheap code on a schedule, reads an external API, and wakes
the AI only for a qualifying logical event. The check time is not the event
identity.

Polling is the Observed path: Helio calls the source. A connected provider can
make this read possible without giving Helio any inbound event subscription.
Do not invent an `api` trigger kind; a read API is implemented with
`--kind poll`.

## Establish that polling can represent the event

Read the official API documentation and one real response. Find:

- a bounded query such as `updated_since`, `created_after`, a delta token, or a
  finite recent-events endpoint;
- a stable item id plus revision, update time, sequence, or event id;
- ordering and pagination behavior;
- rate limits and a polling interval that fits them;
- whether the source is public or needs an authentication payload already
  available to the executor.

Prefer an overlapping read window over a fragile exact cursor when the API
provides stable event identities. For a five-minute poll, reading the previous
ten minutes is often safer than reading exactly the unobservable gap between
two Lambda invocations. The repeated candidates collapse only because their
`fire_key` values stay stable.

Common representable events are:

- **new item:** `source:item_id`;
- **new revision:** `source:item_id:revision` or
  `source:item_id:updated_at`;
- **periodic reminder while a condition remains true:** a time bucket the
  user explicitly asked for, such as `source:item_id:2026-08-22`.

An API that returns only a current snapshot cannot reliably express every
transition. If the user wants "tell me each time this crosses from healthy to
unhealthy," the handler needs a durable previous observation or a source event
history. Lambda globals and `/tmp` are not durable state. A content hash can
identify an unseen snapshot, but it suppresses a later return to an old value;
a timestamp creates duplicate fires. Explain the limitation in plain language
and offer an honest alternative, such as one reminder per day while unhealthy.

## Decide the beginning

Do not let the first deployment accidentally replay the source's whole
history. Choose one policy from the user's wording:

- **future-only:** record or encode a current baseline and ignore older data;
- **current matches:** immediately fire for the bounded set that is already
  true;
- **bounded replay:** process a named recent period such as the last 24 hours.

If future-only cannot be implemented without durable state or a source-side
cursor, say so before deployment. Do not pretend that deployment time itself
is a reliable event boundary.

## Write bounded code

Start from `../templates/poll-handler.mjs` and replace each source-specific
function. Keep these boundaries visible:

1. `fetchCredential()` obtains the one Vault binding once for this invocation
   when the official source contract requires authentication. Leave
   `SOURCE_REQUIRES_CREDENTIAL` false and omit `--credential` for a public
   source; set it true and bind the Vault id for an authenticated source.
2. `observe()` calls the source with a timeout and bounded pagination. Its
   credential argument is `undefined` for a public source.
3. `classify()` returns an array of no more than six logical events according
   to the trigger contract, or an empty array for a near miss. Use a stable
   source order so overlapping windows return the same event identities.
4. `eventIdentity()` derives a stable key from source data and fails closed
   when it cannot.
5. `projectEvent()` removes secrets and irrelevant bulk before the fire.
6. `fire()` uses the fixed Helio callback contract.

Do not put fuzzy AI judgment into the Lambda. Use code for objective gates such
as status, label, amount, or timestamp. When "important" requires context and
judgment, let the trigger wake the executor for the narrowest safe candidate
set and put the judgment in the procedure.

Avoid unbounded fan-out. Fire every qualifying event returned by the bounded
classifier, each with its own stable identity. The template rejects more than
six matches instead of silently dropping the rest. If six may not cover one
poll interval, narrow the source query around a durable cursor or choose a
webhook, provider delta subscription, or purpose-built ingestion path.

Credential reads are reauthorized on every invocation but do not consume the
fire counter. Only `/fire` requests that reach the fixed-window limiter count
against the six-per-minute budget; unauthenticated, malformed, or disabled
requests are rejected earlier. Each event payload is limited to 64 KB.

## Required fixtures

Run local tests for:

- a real-shaped qualifying response;
- two or more qualifying events in one response, with one fire per stable
  identity;
- a near miss from the same endpoint;
- an overlapping response containing the same logical event twice;
- an over-budget response that fails closed rather than dropping matches;
- the chosen first-observation policy;
- pagination stopping at its declared bound;
- timeout, 401/403, 429, 5xx, and malformed JSON;
- proof that no credential, Authorization header, or raw sensitive response is
  logged or included in the event payload.

The same logical event must produce the same `fire_key` in every fixture run.
