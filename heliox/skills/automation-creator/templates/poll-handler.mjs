// Reference poll handler for a Helio automation event trigger.
// Replace the source-specific functions from the trigger contract, test them
// with real-shaped fixtures, package the project root with handler.mjs at its
// root, then deploy:
//   heliox automation trigger create --automation <automation-id> \
//     --kind poll --name <trigger-name> --cron "*/5 * * * ? *" \
//     --code code.zip [--credential <vault-credential-id>]

const REQUEST_TIMEOUT_MS = 5_000;
const MAX_FIRES_PER_INVOCATION = 6;
// Set this from the official source contract before deployment. Public sources
// stay credential-free; authenticated sources fail closed without a binding.
const SOURCE_REQUIRES_CREDENTIAL = false;

export async function handler(invocation) {
  const credential = SOURCE_REQUIRES_CREDENTIAL
    ? await fetchCredential()
    : undefined;
  const observation = await observe(credential, invocation);
  const hits = classify(observation);
  if (!Array.isArray(hits)) {
    throw new Error("classify must return an array");
  }
  if (hits.length > MAX_FIRES_PER_INVOCATION) {
    throw new Error("qualifying events exceed the per-invocation fire budget");
  }

  for (const hit of hits) {
    const identity = eventIdentity(hit);
    const event = projectEvent(hit);
    await fire(
      `e:${process.env.HELIO_AUTOMATION_TRIGGER_ID}:${identity}`,
      event,
    );
  }
  return { fired: hits.length };
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

async function observe(credential, invocation) {
  // Call the documented source endpoint with a bounded lookback, timeout, and
  // pagination limit. Throw on an unreadable source; an API failure is not a
  // quiet observation. Do not log credential or raw sensitive responses.
  void credential;
  void invocation;
  throw new Error("implement observe from the source API contract");
}

function classify(observation) {
  // Return an array of at most MAX_FIRES_PER_INVOCATION logical events. Return
  // [] for a source-shaped near miss. Sort events by a stable source order so
  // overlapping windows produce the same identities in the same order.
  // Objective status/label/amount checks belong here; fuzzy AI judgment
  // belongs in the automation procedure after the executor wakes.
  void observation;
  return [];
}

function eventIdentity(hit) {
  // Derive this from a stable source event id, or resource id plus revision or
  // updated_at. Never use Date.now(), invocation time, a Lambda request id, or
  // a random UUID: those identify the check rather than the external event.
  void hit;
  throw new Error("implement stable eventIdentity from source data");
}

function projectEvent(hit) {
  // Return only the facts and links the executor needs, at most 64 KB of JSON.
  // Remove tokens, authorization fields, and irrelevant raw source data.
  return hit;
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
    throw new Error("fire rate-limited: retry this observation");
  }
  if (!response.ok) throw new Error(`fire failed: ${response.status}`);
  return true;
}
