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

## Boundaries

- The procedure is a document you maintain, not a rules engine or a DAG.
- One automation = one trigger + one procedure + executor(s). Different
  work is a different automation, not branches inside one procedure.
- Cross-run memory lives in the procedure document, not in prior runs —
  write it accordingly.
