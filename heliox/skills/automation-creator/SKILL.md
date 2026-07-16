---
name: automation-creator
description: "Create, evaluate, and maintain Helio automations: AI work that runs later from a schedule, reminder, webhook, or monitored condition. Use whenever the user asks to schedule or automate AI work, send a recurring report or digest, watch or monitor something, notify people when an event happens, follow up later, or inspect and repair an existing automation—even if they never say 'automation'. Do not use for a one-off task to complete now, a human calendar event, or an SOP with no future AI execution. An automation binds a trigger to a self-contained procedure document and one or more AI executors."
user-invocable: false
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox automation --help"
---

# Heliox Automation Creator

Start by reading `../shared/SKILL.md`.

## Take on the work before scheduling it

Treat an automation as work you are agreeing to own, not a form whose schedule
fields need filling. Use this order:

1. understand the requested outcome;
2. do the work once and refine the result;
3. choose evaluation depth and define realistic cases;
4. capture the approved method and create the automation disabled;
5. run the cases, preserving a baseline when improving existing work;
6. grade evidence, aggregate results, and analyze variance or weak checks;
7. show the user, revise, and repeat until satisfied;
8. enable it with the user's approval.

Meet the user where they are. If they already supplied an approved example,
a complete procedure, or an existing automation, start there rather than
repeating work that is already complete.

## Output language

The automation's name, description, and procedure follow the language of the
user's own instruction — never the language of any wrapper, hand-off, or
bootstrap text that surrounds it. The user's instruction is the authoritative
source: when a system-inserted sentence around it is in a different language,
write the artifacts in the instruction's language, not that sentence's.

When the instruction is too short to determine its language (for example a
one-line edit), fall back to the room language, following the brain's existing
rule. This governs the automation artifacts only; conversational replies keep
following the room language, so the two can differ without conflict.

## Creation loop

### 1. Understand and do the work once

Clarify the outcome, inputs, and useful output only where the request is
genuinely ambiguous. Do not lead with cadence, owner, subscribers, or other
setup details.

Execute the work directly in the conversation. If the real event cannot be
produced now, use a clearly labeled historical example or representative
fixture. Put the result in front of the user and revise it until the useful
shape is clear. A real deliverable reveals preferences faster than a setup
questionnaire.

### 2. Decide whether evaluation will pay for itself

After the output is understood, recommend the lightest evaluation that gives
honest confidence:

- **Skip a formal evaluation** when the work is deterministic, low-risk,
  easy to undo, and the approved example already proves the important part.
  Still write a clear success condition. Be explicit that the scheduled
  trigger and executor path remain unverified if the user also skips a
  rehearsal.
- **Lightweight** for simple or subjective work: the approved example plus
  one disabled end-to-end rehearsal is usually enough.
- **Structured** for variable inputs, monitoring, data retrieval, deduping,
  or meaningful no-result behavior: use a representative case, an important
  boundary/no-op case, and a failure case with observable checks.
- **Strict** for external side effects, sensitive data, authentication,
  money, or a broad audience: use fixtures or a sandbox, verify authorization
  and idempotency, cover failure paths, and do not enable until the checks pass.

State the recommendation and reason in one sentence, then let the user choose
a different depth. For example: "This is a read-only digest with variable
input, so I recommend three small cases plus a disabled rehearsal; want that,
a quick rehearsal only, or no formal evaluation?"

Do not force numerical scoring onto taste. Let the user judge subjective
quality; use assertions only for things that can actually be observed, such
as freshness, counts, required fields, destination, terminal state, or number
of deliveries.

When the user chooses structured or strict evaluation, follow the complete
baseline → run → grade → aggregate → analyze → review → revise loop in
[`references/evaluation.md`](references/evaluation.md).

### 3. Write the procedure and create it disabled

The procedure is a fresh executor's complete brief. Write self-contained
markdown from the approved execution, not from an imagined workflow.

Pass the markdown itself to `--procedure`, never its filename. A draft may live
in a local `.md` file while you work, but a later executor cannot follow that
runtime-local path. Put the draft's **contents** in the `--procedure` element
of an argv JSON array; the array file is only `--args-file` transport.

Use the parts of this outline that apply:

```markdown
# <automation name>

## Objective
## Inputs and freshness
## Procedure
## Output and delivery
## Failure and no-result behavior
## Done when
## Evaluation contract (only when structured or strict evaluation is useful)
```

At creation time, state the defaults and ask only for decisions that remain:

- destination defaults to the current conversation;
- owner defaults to the requester (`--owner`, required);
- executor defaults to you;
- subscribers default to none;
- confirm the cadence and any additional audience.

A named clock time is exact: "every day at 9am" means `0 9 * * *`. Add an
off-minute only when the wording is approximate ("every morning", "hourly",
"around lunch") so approximate jobs do not all fire together.

```json
["automation", "create", "<name>", "--cron", "<five-field>", "--owner", "@<requester>", "--procedure", "# <name>\n\n## Objective\n<approved objective>\n\n## Procedure\n<approved steps>"]
```

```bash
heliox --json --args-file /absolute/path/create-automation.json
```

Use `--start "<rfc3339>"` instead of `--cron` for a one-shot. Creation returns
a disabled automation with its trigger and bound procedure document; the CLI
then writes the markdown in a separate request. If that second write fails,
keep the automation disabled, repair its canonical document, and verify it.
Read the returned document before treating the write as proof:

```bash
heliox document read <document_id>
```

The document must contain the approved procedure, not an empty body, local
path, or reference to a draft file. Repair it before rehearsal or enablement.

### 4. Evaluate and iterate at the chosen depth

For a rehearsal, run the disabled automation and inspect the run itself, not
only the polished result:

```bash
heliox automation run <id> --json
heliox automation run show <execution_id> --transcript --json
```

The transcript reveals whether a fresh executor understood the procedure,
used the right inputs, hid a broken dependency behind a fallback, delivered to
the right place, or caused an unintended side effect.

For structured or strict evaluation, use the same loop as skill creation:

1. define realistic cases and observable checks before running them;
2. preserve current behavior as the baseline when maintaining an automation;
3. run the candidate cases, repeating nondeterministic cases when useful;
4. grade each check after execution with exact output or transcript evidence;
5. aggregate results and analyze weak checks, variance, hidden fallbacks, and
   side effects;
6. show the user representative outputs and the evaluation summary;
7. revise the smallest general defect, replay the failure and a representative
   case, and repeat until the user is satisfied;
8. retain stable regressions and latest verified execution IDs in the
   procedure's evaluation contract.

Read [`references/evaluation.md`](references/evaluation.md) for the case
schema, baseline rules, repeated-run policy, grading record, aggregate table,
analyst pass, and human feedback loop.

If the user chooses to skip evaluation, respect that choice. Report exactly
what remains unverified instead of quietly treating creation as proof.

### 5. Hand over

Show the automation ID, schedule or trigger, destination, evaluation result
(if any), and remaining proof gap. Enabling is the user's decision:

```bash
heliox automation update <id> --enable true
```

## Maintaining an automation

Start from current evidence rather than recreating it:

```bash
heliox automation show auto_... --json
heliox document read doc_...
heliox automation runs auto_... --json
heliox automation run show <execution_id> --transcript --json
```

Edit the procedure document in place when the method changes. Preserve the
automation and trigger identities unless the requested change truly requires
new ones. Before editing, retain the current procedure and a safe,
representative run as the baseline; afterward, run the same case against the
candidate.

Use the same proportional evaluation rule for ordinary improvements. A bug is
the exception: turn the observed failure into a regression case, prove the
smallest general fix, and rerun a prior representative case before calling it
resolved. Add the new case to the durable evaluation contract so the next
change replays it. Do not patch only the exact sample that happened to fail.

Useful maintenance commands:

```bash
heliox automation list --json
heliox automation update auto_... --enable false
heliox document edit doc_...
heliox automation run auto_...
```

## Choose the trigger from the source

- Use `--cron` or `--start` when time itself is the trigger.
- Prefer a signed webhook when the source can push a stable event.
- Use a poll trigger when the source cannot push reliably or periodic
  observation is explicitly required.
- For an event trigger, pass the source's stable delivery ID as `fire_key`;
  that is Helio's idempotency boundary for retries and duplicate deliveries.

A phrase such as "checking every five minutes is fine" is a latency budget,
not a reason to ignore a better webhook. For poll/webhook code, signature
verification, idempotency, packaging, local fixtures, deployment, and logs,
read [`references/event-triggers.md`](references/event-triggers.md).

## Executing runs

- Work in the automation's run thread; humans may add useful input there.
- Treat the procedure as the authority for the work and delivery. If it is
  unavailable, report the failure to the owner and stop rather than improvise.
- Deliver short outcomes as messages. Put reports, digests, and analyses in a
  document and share its reference instead of posting a wall of chat text.
- Use judgment with subscribers: a deliberate no-result run may stay silent;
  a failure must not masquerade as "nothing found."
- Cover every terminal state of a watched system, not only success.

## Boundaries

- A procedure is a maintained document, not a rules engine or DAG.
- One automation represents one coherent job. Different work belongs in a
  different automation, not branches hidden inside one procedure.
- Cross-run knowledge belongs in the procedure, not in prior run transcripts.
