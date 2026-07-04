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

You are setting up a job **you run on your own**, on a trigger, by following a
written procedure. You author and own that procedure; the human supervises and
can pause/correct it. This skill is the guided authoring + maintenance loop —
modeled on how a human colleague would write down an SOP, wire it to a
schedule, and refine it over time.

## What an automation is (three orthogonal axes)

| Axis | What | Backed by |
|---|---|---|
| **Trigger** (when) | cron / one-shot fire | the schedule created internally by `heliox automation create` |
| **Procedure** (how) | the step-by-step you re-read **every run** | an automation `document` (`heliox document`, Kind=automation) |
| **Executor** (who) | the AI user(s) that run it (usually you) | AI user handle(s) |

The procedure document **is the memory**. Each fire is a fresh run with no
carried-over conversation — you re-read the procedure and execute it. So write
the procedure to be self-contained: inputs, steps, where the output goes,
what "done" looks like.

## Creating an automation (the loop)

Like authoring a skill: capture intent → create the automation → write the
procedure → confirm → iterate. One `heliox automation create` builds the whole
thing (trigger + procedure document + binding) in one transactional call — you
do NOT create the schedule and document separately; they are internal parts of
the automation, not standalone resources.

### 1. Capture intent
Pull from the conversation: **when** it should run, **what** it should do
(the procedure), **who** runs it (default: you), and **whom it serves** (the
`--owner` — usually the person asking you to set it up). Ask only what's missing.

### 2. Write the procedure, then create the automation (one call)
Author the SOP as **markdown** first — it is what you re-read on every fire, so
make it self-contained (what to gather, the steps in order, the destination
channel, the success check). Pass it as `--procedure` so the document is written
in the same command:
```bash
heliox automation create "<name>" --cron "0 9 * * 1" --owner @<requester> --executor @<you> \
  --procedure "$(cat <<'MD'
# <name>

1. <step one>
2. <step two>
3. Report the result in <channel> with `heliox message send`.
MD
)" --json
# → {id: auto_..., schedule_id: sch_..., document_id: doc_...}
```
This atomically creates the trigger schedule, the procedure document
(Kind=automation, seeded with your markdown), and the automation binding. Flags:
- `--cron "<five-field>"` — recurring trigger. (Local IANA tz is stamped
  server-side.)
- `--start "<rfc3339>"` — a one-shot trigger instead of cron.
- `--executor @<handle>` — the AI that runs it (default: you). Repeat for
  multiple.
- `--owner @<handle>` — **required**: the human this automation serves — usually
  whoever asked you to set it up (their handle is the `username` in the message's
  `from` block); in a group chat where you build it for someone else, use that
  person's handle. This is what lets the owner pause, edit, or delete their own
  automation later. Distinct from `--executor`: owner is the person it acts for,
  executor is the AI that runs it.
- `--procedure "<markdown>"` — the SOP, written into the procedure document at
  create time. Omit it only if you want to fill the document later with
  `heliox document edit <document_id>`.
- created **disabled** by default.

### 3. Confirm + enable + iterate
Show the user the procedure + trigger summary. Refine with
`heliox document edit <document_id> --old "<span>" --new "<span>"` until they're
happy, then enable:
```bash
heliox automation update auto_... --enable true
```
The procedure is the part that matters — every run obeys it.

## Maintaining your automations

```bash
heliox automation list --json                      # your org's automations
heliox automation show auto_... --json             # one automation + its trigger
heliox automation runs auto_... --json             # run history (each run's channel)
heliox automation update auto_... --enable false   # pause (propagates to the schedule)
heliox document edit doc_...                        # revise the procedure
heliox automation run auto_...                     # run once now (manual trigger)
```

When the procedure drifts from reality, **edit the document** — that is how you
maintain the automation. The trigger and executor rarely change; the procedure
evolves.

## Boundaries

- The procedure is a **document you maintain**, not a rules engine or a DAG.
- One automation = one trigger + one procedure + executor(s). Different work →
  a different automation, not branches inside one procedure.
- A fire produces an isolated run (its own channel). Cross-run memory lives in
  the procedure document, not in prior runs — write the procedure accordingly.
