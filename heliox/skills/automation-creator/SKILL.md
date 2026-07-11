---
name: automation-creator
description: "Use to CREATE or MAINTAIN an automation — a triggered/recurring job you (the AI) run on your own (design 246/236/261). An automation = a trigger (when) + a procedure document (how) + executor AI(s) (who). Trigger whenever the user wants to 'set up an automation', 'automate X', a recurring AI task / workflow / SOP, 'every week / each morning do Y', 'follow up on Z on a schedule', or to edit/inspect an existing automation's procedure or run history. You author and maintain the procedure document yourself; the human supervises. Automation is the ONLY way you schedule your own timed work — there is no standalone reminder/cron CLI to hand-roll (design 261 retired it); a recurring or one-shot AI-run job is always an automation."
user-invocable: false
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox automation --help"
---

# Heliox Automation Creator

Start by reading `../shared/SKILL.md`.

## Work first, machinery last

You are a colleague being asked to take on recurring work — not a scheduler
collecting parameters. So behave the way a colleague would: **do the work
once, get it right with the user, and only then freeze it into an
automation.** The automation is a record of work the user has already seen
and approved — never a guess about work that hasn't happened yet.

Everything below follows from that order, and it matters because:

- A person can react to a real deliverable; they cannot meaningfully answer
  abstract questions about the format, length, or audience of something that
  does not exist yet. Asking those upfront turns a conversation into a form.
- The procedure you eventually write is a transcript of an execution the
  user validated — not something imagined and then debugged in production.
- Doing the work directly keeps "is the output right?" separate from "does
  the automation machinery work?" — two different failure modes that are
  miserable to debug when tangled.
- Scheduling and audience are create-time facts. They become easy, natural
  questions at create time and awkward interrogation anywhere earlier.

## The flow

### 1. Understand the work
Clarify the task itself: what the user wants produced, from what inputs.
A round or two of conversation, only if genuinely unclear. No automation
vocabulary belongs here — no cadence, no owner, no subscribers. When someone
says "summarize Hacker News for me every morning", the thing to understand
is what a useful summary looks like to them; the "every morning" part waits
until there is a summary worth scheduling.

### 2. Do it once, now
Execute the task directly in this conversation, as an ordinary request.
Create nothing yet.

### 3. Review the real output together
Put the deliverable in front of the user. Preferences — format, length,
language, structure, message vs document — surface as reactions to actual
material; fold them in and redo until they are satisfied. Several rounds is
normal and cheap; this is the involvement that matters.

### 4. Formalize — only now does the automation exist
Freeze the validated way of working:

- The procedure is what you actually just did: inputs, steps in order, the
  approved output form, the destination, what "done" looks like. Write it as
  self-contained markdown — each future run re-reads it with no memory of
  this conversation.
- The create-time questions are natural now. State the default, then ask:
  "By default this delivers here, to you — anyone else who should get it?"
  (destination + `--subscriber` in one breath). Confirm the cadence. Owner
  defaults to the requester (`--owner`, required — it is what lets them
  pause, edit, or delete their own automation; distinct from `--executor`,
  the AI that runs it, default you).
- A named clock time is the user's time: "every day at 9am" means
  `0 9 * * *`, not 8:52 — the cron you pass is the real schedule, so
  never shift a time they stated. Jitter only when the phrasing is
  genuinely approximate ("every morning", "hourly", "around lunch"):
  don't land those on :00 or :30 — every approximate ask rounded to
  `0 9 * * *` fires at the same instant. Pick an off minute
  (`52 8 * * *`, `7 * * * *`); the user won't notice, the fleet will.

```bash
heliox automation create "<name>" --cron "<five-field>" --owner @<requester> \
  --procedure "<the validated SOP as markdown>" --json
# one transactional call: trigger schedule + procedure document + binding
# → {id: auto_..., schedule_id: sch_..., document_id: doc_...}
# --start "<rfc3339>" for a one-shot instead of --cron; created DISABLED
```

### 5. Hand over
One question: "Want me to run it once end-to-end through the automation so
you can see it, or put it straight to use?"

- Rehearsal: `heliox automation run <id>` works while still disabled — the
  run goes through the real machinery (fire → thread in the automation's
  channel → delivery per procedure), verifying the frozen procedure stands
  on its own. Then enable.
- Straight to use: `heliox automation update <id> --enable true`.

Either way, enabling is the user's call, made about work they have seen.

## Maintaining your automations

```bash
heliox automation list --json                      # your org's automations
heliox automation show auto_... --json             # one automation + its trigger
heliox automation runs auto_... --json             # run history
heliox automation update auto_... --enable false   # pause (propagates to the schedule)
heliox document edit doc_...                       # revise the procedure
heliox automation run auto_...                     # run once now (manual trigger)
```

When the procedure drifts from reality, edit the document — that is how you
maintain an automation. The trigger and executor rarely change; the
procedure evolves.

## Executing runs

- Every run happens in the automation's own channel: the fire posts a run
  header there as a thread root, and you work inside that thread. Humans can
  read the thread and speak in it mid-run — treat their messages as input.
- **The procedure is the run's only authority** on what to do and where to
  deliver. If you cannot read it, report the failure to the owner and stop —
  improvising a destination from the automation's name sends half-baked
  output to an audience that never asked for it.
- Output form follows what the user approved in step 3: short results as a
  chat message; anything long-form — reports, digests, analyses — as a
  document (`heliox document create`, one per run) with its reference shared
  into the destination conversation, never as a wall of chat text.
- Deliver results to subscribers with an ordinary `heliox message send`,
  using your judgment: a run that found nothing need not wake anyone; a real
  finding gets named to the people it concerns.
- When the procedure (or a poll trigger's `shouldFire`) watches something
  for an outcome — a deploy, a feed, a build — cover every terminal state,
  not just the success marker. A watcher that only recognizes "it worked"
  stays silent through a crash or a hang, and silence reads as "still
  fine". Before freezing it, ask: if the thing being watched failed right
  now, would this run say so?

## Event triggers: when a schedule isn't the right "when"

`--cron` (schedule trigger) is the default "when" — it wakes you on a
timer. Two other shapes of "when" don't fit a timer, and design 290 covers
them as a second kind of trigger, `heliox automation trigger`:

- **Cheap, frequent checking that only sometimes needs you** — "tell me
  when the build goes red", "watch this competitor's changelog" — a cron
  automation would cold-start a full session every few minutes just to say
  "nothing changed" almost every time. Use `--kind poll`: EventBridge wakes
  a small Lambda on its own cron; only when *it* decides something's worth
  your attention does it fire the automation.
- **A real external event that can push to you** — a GitHub PR merged, a
  Stripe payment, any webhook-capable source. Use `--kind webhook`: the
  trigger gets a public URL at `webhook.helio.im/<trigger_id>` you configure
  at the source yourself (GitHub webhook settings, etc.) — the platform never
  auto-configures the external side.

Either way, the trigger is not a rules engine or a config — it's a small
Node.js Lambda **you write**: a zip whose root is `handler.mjs` exporting
`handler`. You build it in your own runtime (`npm install`, dependencies
ride along in the zip) and package it yourself (`zip -r code.zip .`) — the
platform only deploys the artifact, never builds or installs it.

```bash
heliox automation trigger create --automation <id> --kind webhook --name <n> --code <file.zip> [--env K=V ...]
heliox automation trigger create --automation <id> --kind poll --cron "*/5 * * * ? *" --code <file.zip>
# no --code: nothing is created — start from templates/webhook-handler.mjs in this skill
```

The fire callback is a contract, not a library call: your `shouldFire`
decides a hit, then your handler POSTs to `process.env.HELIO_AUTOMATION_FIRE_URL`
with `Authorization: Bearer ${process.env.HELIO_AUTOMATION_FIRE_TOKEN}` and body
`{fire_key, event}` — `fire_key` is your idempotency key (prefer the
source's own delivery id), `event` is whatever you want the executor to
see. The platform injects `HELIO_AUTOMATION_FIRE_URL` / `HELIO_AUTOMATION_FIRE_TOKEN` /
`HELIO_AUTOMATION_TRIGGER_ID` into the Lambda automatically; you never see or handle
the token yourself.

**Verify the event yourself — the webhook URL is not a secret.** A
webhook's public address (`webhook.helio.im/<id>`) is discoverable and gets
logged by gateways along the way; the only thing that proves an event is
genuine is a check *you* write in `handler.mjs`. Start from
`templates/webhook-handler.mjs` in this skill (a verification-ready handler)
and use the scheme your source actually offers:

- **Source signs with HMAC (GitHub, Stripe, most dev platforms)** — verify
  its signature header (`X-Hub-Signature-256`, `Stripe-Signature`) against a
  shared secret you set at the source and inject with `--env
  WEBHOOK_SECRET=...`. This is the strong, preferred path, and it's why the
  secret rides in a header the source signs, not in the URL.
- **Source offers no signing** — you fall back to the unguessable URL plus
  the per-trigger rate limit. This is weak (the URL leaks into logs); prefer
  a signing source whenever you can.

How hard you must verify tracks the automation's blast radius: if the
procedure has side effects (sends mail, changes data, spends money),
verification is **mandatory**; a purely read-only/idempotent procedure can
be laxer. `trigger create` prints a warning if it sees no verification in a
webhook handler — heed it.

The platform never inspects or verifies your payloads; it only holds the
Lambda, the event ingress, and a token scoped to firing this one automation.

**Test locally before you deploy.** There is no platform test mode — a
"dry run" fire is indistinguishable from a real one, since the request
body is whatever your code sends. Run `node handler.mjs` against a sample
event yourself first; after deploying, your only observation window is
`heliox automation trigger logs <id>` (CloudWatch).

Fixing a bug in deployed code is an in-place update, not a
delete-and-recreate — the latter mints a new webhook URL and a new token,
breaking anything already configured against the old one:

```bash
heliox automation trigger update <id> --code <file.zip>   # redeploys; URL + fire token unchanged
heliox automation trigger logs <id> [--last 20]            # recent invocations (CloudWatch)
heliox automation run show <execution_id> [--transcript]   # inspect one fire: event in full, +thread timeline
```

## Boundaries

- The procedure is a document you maintain, not a rules engine or a DAG.
- One automation = one trigger + one procedure + executor(s). Different
  work is a different automation, not branches inside one procedure.
- Cross-run memory lives in the procedure document, not in prior runs —
  write it accordingly.
