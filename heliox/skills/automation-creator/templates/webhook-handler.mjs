// Reference webhook handler for a Helio automation event trigger.
// Adapt the provider-specific functions, test with signed fixtures, package the
// project root with handler.mjs at its root, then deploy with a Vault credential:
//   heliox automation trigger create --automation <automation-id> \
//     --name <trigger-name> --kind webhook --code code.zip \
//     --credential <vault-credential-id>

import crypto from "node:crypto";

const REQUEST_TIMEOUT_MS = 5_000;

export async function handler(event) {
  // The public webhook URL is not proof of origin. Fetch only this trigger's
  // bound credential and authenticate the raw body before trusting its fields.
  // Fetch on every invocation so unbind, delete, rotate, or delegation revoke
  // takes effect immediately instead of leaving plaintext in a warm process.
  const credential = await fetchCredential();
  if (!verifyWebhook(event, verificationSecret(credential))) {
    return { fired: false, rejected: "unverified" };
  }

  const hit = await shouldFire(event);
  if (!hit) return { fired: false };

  const deliveryID = eventDeliveryID(event);
  const fired = await fire(
    `e:${process.env.HELIO_AUTOMATION_TRIGGER_ID}:${deliveryID}`,
    hit,
  );
  return { fired };
}

async function fetchCredential() {
  const url = new URL(process.env.HELIO_AUTOMATION_FIRE_URL);
  url.pathname = url.pathname.replace(/\/fire$/, "/credential");
  const response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${process.env.HELIO_AUTOMATION_FIRE_TOKEN}`,
    },
    signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
  });
  if (!response.ok) {
    // Never include the response body: it may contain credential material.
    throw new Error(`credential fetch failed: ${response.status}`);
  }
  return (await response.json()).data;
}

// Adapt this to the actual shape of the one Vault credential bound to the
// trigger. Do not add a second secret through --env.
function verificationSecret(credential) {
  const secret = credential?.webhook_secret;
  if (typeof secret !== "string" || secret.length === 0) {
    throw new Error("bound credential has no webhook_secret");
  }
  return secret;
}

// Default example: GitHub X-Hub-Signature-256. Replace this whole function
// with the provider's documented scheme. Providers such as Stripe also require
// timestamp parsing and replay-window validation.
function verifyWebhook(event, secret) {
  const signature = event.headers?.["x-hub-signature-256"];
  if (!signature) return false;

  const rawBody = event.isBase64Encoded
    ? Buffer.from(event.body ?? "", "base64")
    : Buffer.from(event.body ?? "");
  const expected =
    "sha256=" + crypto.createHmac("sha256", secret).update(rawBody).digest("hex");
  return (
    signature.length === expected.length &&
    crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expected))
  );
}

async function shouldFire(event) {
  // Parse only after verifyWebhook succeeds. Return null for a source-shaped
  // near miss, or a minimal object containing only what the executor needs.
  // Validate every required business id and predicate field before filtering;
  // never coerce undefined, null, or an object into an apparent stable value.
  // Never include signatures, credentials, or an unbounded raw payload.
  void event;
  return null;
}

function eventDeliveryID(event) {
  // Implement the source's stable delivery identity. A gateway request id,
  // invocation time, or random UUID would duplicate fires on provider retries.
  const deliveryID = event.headers?.["x-github-delivery"];
  if (!deliveryID) throw new Error("missing stable source delivery id");
  return deliveryID;
}

async function fire(fireKey, event) {
  const response = await fetch(process.env.HELIO_AUTOMATION_FIRE_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${process.env.HELIO_AUTOMATION_FIRE_TOKEN}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ fire_key: fireKey, event }),
    signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
  });
  if (response.status === 429) {
    throw new Error("fire rate-limited: retry this delivery");
  }
  if (!response.ok) throw new Error(`fire failed: ${response.status}`);
  return true;
}
