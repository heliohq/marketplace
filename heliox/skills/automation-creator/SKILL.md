---
name: automation-creator
description: "Create, evaluate, and maintain Helio automations: AI work that runs later from a schedule, reminder, webhook, or monitored condition. Use whenever the user asks to schedule or automate AI work, send a recurring report or digest, watch or monitor something, notify people when an event happens, follow up later, or inspect and repair an existing automation—even if they never say 'automation'. Do not use for a one-off task to complete now, a human calendar event, or an SOP with no future AI execution. An automation binds a trigger to a self-contained procedure document and one or more AI executors."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox automation --help"
---

# Heliox Automation Creator

## Model

- An automation = a trigger (cron / one-shot / event) + a procedure document + AI executors. Verbs address it by 24-hex id; people are `@handle`, channels `#name` — reads return the vocabulary the flags take.
- Created DISABLED, always. Enabling is the user's decision after proof: `automation update <id> --enable true`.
- The procedure document is a fresh executor's complete brief (`heliox document read|edit <document_id>`). Cross-run knowledge lives there, not in prior transcripts.
- `--owner @handle` (required) = the human it serves; lets them pause/edit/delete later. Subscribers want run results; the owner is always implicit (`automation subscriber list|add|remove`).
- Run lifecycle: fired → started → success | failed | skipped (or died). The run's process has one source of truth — its thread in the automation channel. `run show <execution_id>` is the fire record (including how it fired — schedule / trigger / manual); `--transcript` renders the thread's newest messages (`--tail N`, default 30 — the result and terminal state live at the end) and says so when older ones are omitted.
- Reads (`list`/`show`/`runs`): plain text is the cheap recall mode; add `--json` when acting on field values.

## Do the work once first

An automation is work you agree to own, not a form whose schedule fields need filling. Execute the request once in the conversation first (a labeled historical example if the real event can't be produced now) and refine it with the user — a real deliverable reveals preferences faster than a setup questionnaire. Then capture the approved method as the procedure. If the user brings an approved example or existing automation, start there.

## Create

```json
["automation", "create", "<name>", "--cron", "0 9 * * 1-5", "--owner", "@<requester>",
 "--procedure", "# <name>\n\n## Objective\n<approved objective>\n\n## Procedure\n<approved steps>"]
```

```bash
heliox --json --args-file /absolute/path/create-automation.json
```

- `--cron` XOR `--start "<rfc3339>"` (one-shot). A named clock time is exact ("every day at 9am" = `0 9 * * *`); add an off-minute only for approximate wording ("every morning") so approximate jobs don't all fire together.
- State the defaults, ask only what remains: destination = this conversation, owner = requester, executor = you, subscribers = none; confirm cadence.
- `--procedure` takes the markdown BODY, never a filename — a later executor cannot read a runtime-local path. Draft in a local `.md` if you like, but paste its contents into the argv JSON; the file is only `--args-file` transport.
- The procedure write is a second request after create. Verify: `heliox document read <document_id>` must show the approved procedure, not an empty body or a path. Repair before rehearsal or enablement.

## The procedure document

Self-contained markdown from the approved execution, using the parts that apply:

```markdown
# <name>
## Objective
## Inputs and freshness
## Procedure
## Output and delivery
## Failure and no-result behavior
## Done when
```

For recurring scans/digests/watches, `## Inputs and freshness` pins the read scope: exact sources + filters derived from the cadence (`--channel`, `--status`, `--since` of one cadence period — a daily scan reads the last day, not everything). A bounded read that finds nothing IS the no-result path; never page past the window or drop filters because a period was quiet. Keep eval cases, grades, and execution ids OUT of the procedure — authoring evidence, not per-run instructions.

## Evaluate before enabling

Recommend the lightest depth that gives honest confidence — one sentence with the reason — and let the user choose:

| Depth | When | What it takes |
| --- | --- | --- |
| skip | deterministic, low-risk, undoable; the approved example proves it | a success condition; note the trigger path stays unverified |
| light | simple or subjective work | approved example + one disabled rehearsal |
| structured | variable inputs, monitoring, dedup, meaningful no-result | representative + boundary/no-op + failure case, observable checks |
| strict | side effects, sensitive data, auth, money, broad audience | fixtures/sandbox; verify authorization, idempotency, failures; no enable until green |

Assertions only for observables (freshness, counts, destination, delivery totals); the user judges taste — never force numeric scores onto it. Rehearse while still disabled:

```bash
heliox automation run <id>
heliox automation run show <execution_id> --transcript --json
```

Transcript inspection is an evidence read, so it takes `--json`: cards, approvals, and attachments have no text twin, and grading a rehearsal without them can pass a broken run.

The transcript shows whether a FRESH executor understood the procedure, hid a broken dependency behind a fallback, or delivered wrong. For structured/strict, follow the baseline → run → grade → aggregate → analyze → review loop in [`references/evaluation.md`](references/evaluation.md). If the user skips evaluation, respect it — and report exactly what stays unverified.

Hand over: id, trigger, destination, evaluation result, remaining proof gap. Enabling is the user's call.

## Executing a run

- Work in the run's own thread — it is the run's audit record, never left empty. Long output goes in a document; its reference goes in the thread.
- The procedure is the authority. If unreadable, report to the owner and stop — don't improvise.
- Finalize with exactly one terminal verb; the worth-sharing judgment is success-vs-skip, not per-subscriber:

```bash
heliox automation run success <execution_id>                                   # needs: result in thread + digest DM to EVERY subscriber first
heliox automation run failed <execution_id> --reason "<what broke>"            # needs: owner DM'd what broke (thread mention doesn't count)
heliox automation run skip <execution_id> --reason "<checked what; why quiet>" # quiet run: one-line all-clear in thread, no digests
```

`--reason` is required on `failed`/`skip` — omitting it leaves the run unfinalized. A failure must never masquerade as "nothing found"; cover every terminal state of a watched system.

## Maintain

```bash
heliox automation list                      # ID STATUS NAME OWNER NEXT_RUN DOCUMENT
heliox automation show <id>
heliox automation runs <id>                 # ID FIRED_AT SOURCE STATUS ...; newest 10, --limit up to 100; a full page may continue
heliox automation run show <execution_id> --transcript --tail 30 --json
heliox document edit <document_id>
heliox automation update <id> --enable false
```

Start from current evidence, not recreation. Edit the bound procedure in place; preserve automation and trigger identities unless the change truly requires new ones. Before a behavioral edit, keep the current procedure + a representative run as baseline, then run the same case against the candidate. A production bug: turn the failure into a regression case, prove the smallest general fix, replay a prior representative case — never patch only the sample that failed. Loop details: [`references/evaluation.md`](references/evaluation.md).

## Event triggers

Choose from the source, not the phrasing: time itself → `--cron`/`--start`; source pushes a signed event → webhook; no reliable push → poll. "Checking every five minutes is fine" is a latency budget, not a webhook veto. Pass the source's stable delivery id as `fire_key` — the idempotency boundary for retries. Handler contract, signature verification, packaging, fixtures, deploy, logs: [`references/event-triggers.md`](references/event-triggers.md).

## Output language

The automation's name, description, and procedure follow the language of the user's own instruction — never a wrapper or bootstrap sentence around it; a mixed instruction follows its dominant language. Too short to tell (a one-line edit)? Fall back to the room language per the brain's rule. Artifacts only — conversational replies keep the room language, so the two can differ.

## Boundaries

- A procedure is a maintained document, not a rules engine or DAG.
- One automation = one coherent job; different work is a different automation, not hidden branches.
