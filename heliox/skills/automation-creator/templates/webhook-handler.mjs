// webhook-handler.mjs — reference handler for a Helio automation *event
// trigger. Copy this into your trigger project, keep the
// fire-callback contract as-is, and fill in the two functions you own:
// verifyWebhook() and shouldFire(). Then package the project root (which must
// contain handler.mjs) as a zip and deploy:
//   heliox automation trigger create --kind webhook --code code.zip --env WEBHOOK_SECRET=...
//
// Use the public URL returned by `trigger create` — it is NOT a secret. Anyone
// who learns it can POST to it, so the only thing
// that proves an event is genuine is verifyWebhook(). Never skip it for a
// webhook whose automation has side effects (sends mail, changes data, spends
// money); a read-only/idempotent automation can be laxer, but verifying is the
// default.

import crypto from "node:crypto";

export async function handler(event) {
  // 1) Authenticate the event before trusting anything in it.
  if (!verifyWebhook(event)) return { fired: false, rejected: "unverified" };

  // 2) Your judgment: is this event worth waking the executor?
  const hit = await shouldFire(event);
  if (!hit) return { fired: false };

  // 3) Fire. This contract is fixed; the platform injects these env vars.
  const res = await fetch(process.env.HELIO_AUTOMATION_FIRE_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${process.env.HELIO_AUTOMATION_FIRE_TOKEN}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      fire_key: `e:${process.env.HELIO_AUTOMATION_TRIGGER_ID}:${eventDeliveryID(event)}`,
      event: hit,
    }),
  });
  if (res.status === 429) {
    console.warn("fire rate-limited, event dropped"); // visible via `trigger logs`
  } else if (!res.ok) {
    throw new Error(`fire failed: ${res.status}`);
  }
  return { fired: res.ok };
}

// verifyWebhook — prove the event really came from your source, using the
// SOURCE'S OWN signature scheme. The shared secret is configured at the source
// (e.g. GitHub webhook settings) and injected here via
// `trigger create --env WEBHOOK_SECRET=...`. Default shows GitHub; swap in your
// source's scheme from the variants below.
function verifyWebhook(event) {
  const secret = process.env.WEBHOOK_SECRET;
  if (!secret) return false; // fail closed: no secret configured => never fire

  // GitHub: X-Hub-Signature-256 = "sha256=" + HMAC-SHA256(secret, rawBody)
  const sig = event.headers?.["x-hub-signature-256"];
  if (!sig) return false;
  const expected =
    "sha256=" +
    crypto.createHmac("sha256", secret).update(event.body ?? "").digest("hex");
  return (
    sig.length === expected.length &&
    crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(expected))
  );

  // Variants (replace the GitHub block above with the one matching your source):
  //
  //   Stripe — parse `t=` and `v1=` from the `stripe-signature` header, compute
  //   HMAC-SHA256(secret, `${t}.${rawBody}`), compare against v1, and reject if
  //   |now - t| exceeds ~5 minutes (replay window).
  //
  //   poll trigger (no inbound HTTP event, nothing to verify):
  //     return true;
}

async function shouldFire(event) {
  // Your judgment: filter noise, call an API, compare thresholds — whatever
  // decides "this is worth an executor run". Return null to skip, or an object
  // to hand the executor as `event`.
  //   webhook: event = the API Gateway HTTP event (headers/body)
  //   poll:    event = the EventBridge scheduled event
  return null;
}

function eventDeliveryID(event) {
  // Idempotency key: prefer the source's own delivery id (e.g. GitHub's
  // X-GitHub-Delivery header), fall back to the Lambda request id.
  return (
    event?.headers?.["x-github-delivery"] ??
    event?.requestContext?.requestId ??
    crypto.randomUUID()
  );
}
