---
name: automation-refiner
description: "Refine a Helio automation that already exists: validate a newly created one before it goes live, repair it when it stopped working, change what a recurring job produces or who receives it, or review how an automation has been running and improve it. Use whenever someone is unhappy with a recurring report, a scheduled job broke or started returning errors, a run needs rehearsing before enablement, or a run exposed a problem in its own procedure—even if they never say 'automation'. Do not use to create one from scratch; that is automation-creator."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox automation --help"
---

# Heliox Automation Refiner

This skill handles everything that happens to an automation after it exists — validating it, repairing it when it decays, changing what it does, and improving it across runs. Creating an automation from scratch is `heliox:automation-creator`.

Refining an automation goes like this:

- Gather the evidence — what actually happened, in its own words
- Find out whether you can fix it yourself, or whether it needs a person
- Decide which layer you are changing: how it works, or what it is for
- Make the change in place
- Prove it, while the automation is still disabled if you can
- Leave a trace and tell the owner

Three entry points feed the same loop. The only difference between them is where the evidence comes from. Once you have it, stages 2 through 6 are identical regardless of entry.

## 1. Gather the evidence

### Entry 1 — the user asked for a change

The first thing to establish is whether they are unhappy about this one result, or about every run from now on. A complaint about one result may not require any change to the procedure — the run may have been correct and the output simply surprising. A complaint about every run is a procedure change.

The run channel is visible to the whole org, so the person speaking up may not be the owner. Changes ultimately serve the owner's intent, so when the request comes from someone else, confirm with the owner before editing.

### Entry 2 — you are testing, or you saw something wrong

A run executes in its own thread and its outcome will not appear in front of you on its own. You need to go and get it:

```bash
heliox automation runs <id>
heliox automation run show <execution_id> --transcript --json
```

The `--json` flag matters: cards, approvals, and attachments have no plain-text equivalent, and without it you may give a broken run a passing grade because you only saw the text portion of its output.

Two risk levels shape how freely you can iterate:

- **still disabled** — the automation has never been enabled, or you disabled it for testing. Nothing fires on its own, so you can iterate at your own pace. A manual run is still a real run, though — it delivers to every subscriber in the snapshot (see step 5 for how to rehearse without that).
- **already enabled** — the next scheduled run will deliver real output to real subscribers. Changes need to be conservative, and you should tell the owner what you changed and why before the next run fires.

### Entry 3 — looking back across runs

A single run cannot distinguish a one-off glitch from a pattern. A source that fails today and recovers tomorrow looks the same in one run as a source that fails every week — but the first does not justify a procedure change while the second demands one. Separating the occasional from the systemic requires a cross-run perspective.

When the user asks for a review ("look at how this has been running lately"), gather the evidence through the `runs` and `run show` commands above — list recent executions, inspect representative transcripts, and look for repeated patterns versus one-off glitches.

The automatic trigger — something that wakes you up after N runs to do this review without being asked — is not yet enabled. Until it is, cross-run reviews happen when the user requests them.

## 2. Find out whether you can fix it yourself

Your default is to fix it. An automation decays naturally as the services, channels, and people it depends on change around it. The owner created it so they would not have to watch those things — repairing that decay is your job, and escalating is the fallback, not the first move.

The question is simple: can the problem be solved by editing the procedure?

| What actually went wrong | Can you fix it? | What to do |
| --- | --- | --- |
| The service it reads changed its API, its URL, or its response shape | Yes | Update the steps to match the new interface |
| A channel, document, or person it points at was renamed or moved | Yes | Update the reference to the current name or location |
| A step was too vague and the run went sideways | Yes | Make the step explicit enough that the next run cannot misread it |
| Expired credentials, or access that was revoked | No | Tell the owner, name the specific access you need |
| The source is gone and picking a replacement is a decision only a person can make | No | Tell the owner, bring your recommendation for what to use instead |
| The source failed just this once | Do not change it | Report this run as failed and move on |

When you escalate, say why you cannot fix it yourself — whether it is a missing permission, a revoked credential, or a judgment call that needs a person. "I cannot fix this" without a reason gives the owner nothing to act on.

The last row deserves emphasis: when a source fails once and recovers, do not touch the procedure. Adding a workaround for a one-off failure means that workaround stays in the procedure permanently, and from that point forward it hides the real health of the automation. You can no longer tell whether the source is stable or not, because the procedure silently papers over its failures. A single bad run is a failed run, not a reason to redesign. Repeated failures across runs are decay — and decay belongs in the rows above.

## 3. Decide which layer you are changing

**Method layer** — how the automation reads its sources, where it reads from, how it formats the output, how it decides a period was quiet, how it retries on transient errors. These are the means of getting the owner's intended result. You can change them yourself.

**Intent layer** — what the automation produces, who receives it, what counts as good enough, what counts as something worth raising to subscribers. These are the things the owner agreed to when the automation was created. Bring your recommendation back to the owner rather than changing them on your own.

Every self-edit requires evidence: change something because of something you observed — a step that failed, a source that returned an unexpected shape, a format that lost information — not because you think it could be nicer. No one is watching in real time to catch a well-intentioned tweak that silently changes the output, and the next run delivers directly to subscribers.

Bad:
> "The summary could be more concise. I will tighten the formatting instructions."

Good:
> "Run e-4f92 produced a 1,200-word summary for a period with two minor updates. The procedure says 'summarize,' but does not cap length relative to the input volume. I will add a guideline: keep the summary under 200 words when the period has fewer than five items."

Bad:
> "I will switch the source from the REST API to the GraphQL endpoint because it returns richer data."

Good:
> "Run e-7a01 failed because the REST endpoint now returns 404 on /v2/reports. The service moved this data to /v3/reports with a different response shape. I will update the procedure to use the new endpoint and adjust the field mapping."

## 4. Make the change

Edit the bound procedure document in place: `heliox document edit <document_id>`. Preserve the automation and trigger identities — rebuilding them from scratch discards the run history that future cross-run reviews depend on. Recreate only when the change genuinely requires a new automation (a different job, a different cadence, a different owner).

Not everything lives in that document, and editing the wrong place fails silently — the edit succeeds, and the behaviour does not change:

- **Who receives the results** is stored on the automation, not in the procedure. Writing "send this to Sarah too" into the steps changes nothing: every fire snapshots the stored audience. Use `heliox automation subscriber add <id> @sarah` or `heliox automation subscriber remove <id> @sarah`, or replace the whole set with `heliox automation update <id> --subscriber <handles>`. Check the result with `heliox automation subscriber list <id>` — it shows the effective audience including the owner, who is always implicit. Removals matter most here: someone the owner wanted taken off the list keeps receiving the output until this command runs.
- **What an event trigger's handler code does** lives in the deployed handler, not in the procedure. The deployed artifact is the source of truth — a refinement often runs in a later runtime where the original source is not on disk, and rebuilding from the template silently discards whatever the handler accumulated (signature verification most dangerously). Fetch the current artifact first with `heliox automation trigger show <trigger-id> --code`, unpack the downloaded zip, make your edits to `handler.mjs`, repackage it, then redeploy with `heliox automation trigger update <trigger-id> --code <handler.zip>`. The `--code` flag is what redeploys the handler in place; without it the command is metadata-only and the broken handler keeps running. The in-place redeploy preserves the trigger's stable URL and token.
- **The schedule itself** lives on the underlying trigger, not in the procedure document. The CLI does not currently support changing the cron expression on an existing scheduled automation — `heliox automation update` accepts `--name`, `--executor`, `--subscriber`, and `--enable`, but not `--cron`. If the owner asks to change the cadence, the current path is: create a new automation with the updated schedule, validate it while it is still disabled, disable the old one with `heliox automation update <old-id> --enable false`, then enable the replacement — in that order, because enabling the replacement before disabling the original leaves both schedules live and fires the same job twice, including every external side effect. Disabling beats deleting because the old run history stays readable and the cutover is reversible if the replacement misbehaves. Writing "run at 8:30 instead of 9:00" into the procedure does not change when the trigger fires.

Before editing, capture your baseline: the current procedure text and at least one representative recent run. You need both so that after the change you can tell whether things improved, and if something regresses you can trace it back.

## 5. Prove it

How much proof a change needs depends on what changed and what is at stake. Give the user a one-sentence recommendation with a reason, and let them decide:

- A typo fix or a renamed channel reference is low-risk — a single readback of the procedure may be enough.
- A logic change to the procedure (new steps, changed filters, different formatting) benefits from at least one rehearsal run while the automation is still disabled.
- A change prompted by a production failure should reproduce the failure on the current procedure, apply the smallest general fix, then replay both the failing case and a representative successful case to confirm the fix does not regress normal output.
- A behavioral redesign — changing what the automation produces or how it evaluates its sources — calls for the full evaluation loop.

When you can rehearse, do it while the automation is disabled: `heliox automation run <id>`, then fetch the transcript through Entry 2's commands to read the result. Disabling stops the schedule from firing on its own, but a manual run is still a real run — a fresh executor wakes up in its own thread and follows the full contract, including delivering the result to every subscriber in the fired-time snapshot. You cannot intervene in that delivery from the outside.

If the automation has no subscribers yet, a manual run reaches nobody but the owner — rehearse freely. If it has subscribers, a manual run will deliver to them. To rehearse without mailing subscribers, clear the audience first (`heliox automation update <id> --subscriber ""`), run the rehearsal, then restore the original audience (`heliox automation update <id> --subscriber <handles>`). Record the original subscriber list before clearing — restoring from memory after several iterations is how people get dropped.

For the full structured evaluation loop — cases, baselines, grading, aggregation, and revision — read [`references/evaluation.md`](references/evaluation.md).

## 6. Leave a trace and tell the owner

Record what you changed, why you changed it, and which run or observation drove the change. A procedure edit with no explanation is a procedure that the next maintainer (including your future self) cannot reason about.

Tell the owner — especially when the automation is already enabled, because the next run will execute the new procedure. For method-layer changes, a brief message with the what and why is enough. For intent-layer changes, wait for the owner's approval before writing the edit; the owner's sign-off is what makes an intent change legitimate.

## Executing one run

When you have been woken to execute a run rather than to change the automation, follow [`references/executing-a-run.md`](references/executing-a-run.md).

## Output language

- Name, description, and procedure follow the user's own instruction language — not a wrapper sentence around it. A mixed-language instruction follows its dominant language.
- If the instruction is too short to tell (a one-line edit), fall back to the language the conversation is in.
- This applies to artifacts only — conversational replies stay in the conversation's language, so the two can differ.

## Boundaries

A procedure is a maintained document, not a rule engine. It describes what to do in prose that an AI executor reads and follows. If a change turns the procedure into conditional logic or branching control flow, the work should be code, not a procedure edit.

One automation is one job. If what the user is asking for is actually a different job — different sources, different output, different audience — that is a new automation, and the path back is `heliox:automation-creator`.

---

Keep these six steps in your working list so you do not skip the evidence-gathering or the owner notification:

1. Gather the evidence
2. Find out whether you can fix it yourself
3. Decide which layer you are changing
4. Make the change
5. Prove it
6. Leave a trace and tell the owner

Please add these steps to your todo list before you start so nothing gets skipped.
