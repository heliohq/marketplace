---
name: automation-creator
description: "Create a Helio automation: AI work that runs later from a schedule, reminder, webhook, or monitored condition. Use whenever the user asks to schedule or automate AI work, send a recurring report or digest, watch or monitor something, notify people when an event happens, or follow up later, even if they never say 'automation'. Do not use for a one-off task to complete now, a human calendar event, or an SOP with no future AI execution. For an automation from a prior conversation — whether live, disabled, or never enabled — use automation-refiner instead."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox automation --help"
---

# Heliox Automation Creator

This skill turns a request into an automation: a trigger, a procedure document, and an AI that executes it. It does not stop until that automation has been run against real data and the user has seen the results. Everything after it goes live belongs to `heliox:automation-refiner`, which repairs it when it decays, changes what it produces, and reviews how it has been running.

Creating an automation goes like this:

- Pin down what the user actually wants: what it produces, when it runs, who receives it
- Check the ground before you promise anything
- Do the work once, right here in the conversation, and get their sign-off on the real output
- Write down what happens on the paths you did not just see
- Write the procedure
- Create it with the trigger the signal calls for (cron: disabled until armed; one-shot: enabled, it fires at its start)
- Run it against real data and grade what comes back
- Improve it until it holds
- Hand it over, naming what is still unproven

Steps 7 and 8 are the ones that get skipped. At creation time you have zero run data, so everything you believe about this automation is a prediction; those two steps are where predictions become evidence, and they are cheap: you do not have to wait for next Monday to see what next Monday looks like.

Work out where the user already is before you start. Three common openings:

1. Nothing exists yet. Start at step 1. This is the default path.
2. The user brought an approved example, pasted or described. Step 3 is already done; align on any gaps, then move to step 4.
3. A built-in template fits. `heliox automation catalog list` / `show <id>` holds proven recurring procedures (daily priorities, weekly reflection, inbox triage, …) — check it before authoring from scratch, and when you notice a recurring need nobody has named yet, propose the matching template in one concrete sentence: what would run, when, and what they'd receive. On their explicit yes, fork it through this skill's normal flow — `show` prints the full procedure markdown to pass to `automation create --procedure`, with the template's cron and the owner's real IANA timezone in place of the catalog's `owner-local` sentinel. Only a person clicking Start in the gallery is outside this skill; nothing installs a template on someone's behalf without their agreement, and a declined proposal stays declined.

## Talking to the user

Some of this vocabulary is yours, not theirs. Two rules.

Always translate the words below. They are internal names for things the user already understands:

| You say to the CLI | You say to the user |
| --- | --- |
| procedure | the steps |
| executor | who runs it |
| subscriber | who gets the results |
| disabled | not turned on yet |

Introduce these only if the user reaches for them first: cron expression, webhook, fire key, idempotency, subscriber snapshot, backtest. They are precise and worth using once they are on the table, but leading with them turns a conversation into a form.

The rest is register. "Every weekday at 8:30" needs no translation; `30 8 * * 1-5` does. Say what you did in their terms and keep the expression to yourself unless they ask to see it. If they open with "set up a cron for", match them.

## 1. Pin down what they want

Mine the conversation before you ask anything. The most common way this skill gets invoked is "that thing you just did, do it every week," and when that happens the conversation you are already in *is* the specification: the tools you used, the order you used them in, the corrections the user made along the way, the format they reacted well to. Extract those answers first, put them in front of the user as a short list to confirm, and only ask about what is genuinely missing. Re-interviewing someone who just told you everything reads as not having listened.

Four questions drive the rest of the process. Ask what remains of them in the conversation, not as a form, and explain why each answer matters:

1. What should this automation produce? A summary, a status report, a notification, a document. This sets the shape of the procedure and the output format.
2. What makes it run? Ask for the occasion, not a cron expression: "every Monday morning before standup" or "whenever a new issue is labeled urgent." Converting that into a cron string or a webhook filter is your job, not the user's.
3. What does the result look like, and who receives it? This determines the output section of the procedure and whether you need subscribers.
4. What happens if it gets this wrong while nobody is watching? A reminder posted into a private chat is worth one answer; an email to a customer, a payment, or a public post is worth another. You are asking for the blast radius, and it is load-bearing twice over: it sets how hard you test in step 7, and it is the thing you must name out loud at handover in step 9.

State the sensible defaults and only ask about what remains. Destination is the current conversation, owner is the person asking, executor is you, and there are no additional subscribers beyond the owner, who receives the result of successful runs and a notice when one fails. Quiet runs notify nobody.

Do not create anything until all four questions have answers. A half-understood request becomes a half-correct procedure, and unlike a one-off task, this one will run on its own, repeatedly, without anyone watching.

## 2. Check the ground

Go look at the things this automation depends on before you commit to anything about them. Four checks, all of which you run yourself rather than asking the user.

Is the source actually reachable, and does it return what everyone assumes it returns? Read it once. A channel that was renamed, an endpoint that moved, or a report that no longer has the column the user described is cheaper to find now than in step 3.

Does the source push events? Step 6 prefers a webhook over polling whenever one exists, and whether this source supports webhooks is something you find out by checking its documentation or its settings, not by asking the user.

Will the executor be able to do this? You are about to do the work yourself, in this conversation, with the tools and credentials *you* have connected right now. The automation will run later as the executor. If those are not the same identity, or the executor lacks an integration or a vault credential you are about to use, the run in step 7 is where you find out, unless you check here. Name the specific access needed and get it arranged rather than designing around a gap you have not confirmed.

Does the destination exist? The channel, document, or address the results go to.

Does one of these already run? `heliox automation list --json` before you create a recurring one. A second automation covering the same ground is worse than none: both fire, the owner gets two digests that disagree, and neither is obviously the stale one. If something close already exists, refine it (`heliox:automation-refiner`) instead of adding a rival.

Come to the user with this already done. Every check you skip becomes a question they have to answer or a failure they have to watch.

## 3. Do the work once, here

At creation time you have zero run data. A real output exposes preferences, format issues, and missing context faster than any questionnaire.

Before you execute anything, look at the blast radius from question 4. If the
work has an outward or irreversible effect, sending mail, filing a ticket,
posting somewhere public, moving money, then doing it "once, here" is doing it
for real, to real people, before any of the containment in step 7 exists. Point
that step at yourself or a scratch destination first, exactly as step 7 will,
or ask the user to approve this single live execution and say plainly what it
will do. Do not perform it unannounced because the request happened to be
executable.

With that settled, execute the request once in the current conversation. If the
real event cannot be produced right now (the source only updates on weekdays,
say), use a clearly labeled historical example and tell the user it is
historical.

Show the output to the user and get their sign-off. This output is the standard everything later is measured against: step 7 asks whether a fresh executor, reading only the procedure, reproduces it.

Pay attention to what they change. Their corrections are the real specification, but each correction is about this one output while you are writing something that runs forever, so ask which it is. "Drop the Bugs column" might mean *this week's bugs column was empty* or *never show bugs*. Those produce different procedures, and only one of them is right.

Bad:
> The user removed the "Blocked" section from the draft, so the procedure says: "Do not include a Blocked section."

Good:
> The user removed the "Blocked" section from the draft. Asked whether to drop it always or only when empty; they said only when empty. The procedure says: "Include a Blocked section only when at least one item is blocked; omit the heading entirely otherwise."

If the user brought an approved example or has an existing automation to work from, start there instead of redoing the work.

## 4. Write down the paths you did not see

Step 3 exercised exactly one path: the one where everything worked and data was available. But an automation runs unattended, often at odd hours, and the paths you did not see are the ones that will cause problems. Every procedure needs explicit handling for these four situations.

These four are also your test cases. In step 7 you will run them rather than just describe them, so write each one specifically enough that you could check whether a run obeyed it.

### Nothing found

A bounded read that returns no results within the time window is a normal outcome, "nothing happened this period". It is not an error, and not a reason to widen the search. The procedure should spell out what "nothing found" looks like and what to report.

Bad:
> "If no results are found, try expanding the search window or removing filters."

Good:
> "If no messages match the filter in the last 24 hours, post a one-line summary in the run's own thread: 'No new incidents since yesterday's report.' Do not extend the window or loosen the filter. A quiet period is a valid result, so close with `heliox automation run skip <execution_id> --reason \"checked #incidents for the last 24h; no matching messages\"`."

The key distinction: an empty result from looking at the right window is data, not a malfunction. Dropping filters or paging backwards to force a non-empty result is a bug, because it turns "nothing to report" into a stale or misleading output.

### A step fails

A mid-procedure failure (API error, permission denied, unexpected format) should not silently swallow the error or produce a partial output without flagging it. The procedure should name what counts as a failure and who to notify.

Bad:
> "Handle errors appropriately."

Good:
> "If the GitHub API returns a non-200 status, stop the run, send a DM to the owner with the status code and endpoint, and finalize the run as failed with the reason 'GitHub API error: {status} on {endpoint}'."

### Partial success

Some sources may return data for three out of four channels, or a report may render correctly except for one chart. The procedure should define whether a partial result ships with a note about what is missing, or counts as a failure.

Bad:
> "If some data sources are unavailable, include whatever data is available."

Good:
> "If one of the three source channels returns an error while the others succeed, include the data from the working channels and add a note at the top: 'Data from #frontend-alerts was unavailable, so this report covers the other two channels only.' Finalize as success. If two or more channels fail, finalize as failed and DM the owner with the list of errors."

### The source is unreachable

DNS failures, expired tokens, rate limits, and maintenance windows all look different from "nothing found." The procedure should distinguish "I checked and nothing was there" from "I could not check at all", and say what to do in the second case. Retry? Notify? Skip?

Bad:
> "If the source is unavailable, retry later."

Good:
> "If the source returns a connection error or a 5xx status, wait 60 seconds and retry once. If the retry also fails, DM the owner with the error and finalize the run as failed with reason 'Source unreachable: {error}'. Do not produce a partial report from cached data."

When working through these paths with the user, ask concrete questions: "What should happen if the Slack channel has zero messages this week?", "If the GitHub API returns an error halfway through, should the automation stop completely or try to finish with whatever it has?", "If one of your three data sources fails but the other two work, do you want the partial report or nothing?", or "If the API is down at 3 AM, should it retry or just tell you in the morning?" Their answers become the procedure's failure and no-result sections.

## 5. Write the procedure

The procedure carries the whole job: the trigger decides *when* something happens; the procedure decides *what*. It is read from scratch by an executor who was not in this conversation, has none of your context, and cannot ask you a follow-up question.

### The shape

```markdown
# <name>
## Objective            (required)
## Inputs and freshness  (required for anything that reads a source)
## Procedure            (required)
## Output and delivery  (required)
## Failure and no-result behavior   (required)
## Done when            (required)
```

Every section is required. `## Failure and no-result behavior` is the output of step 4: it governs the runs nobody is watching, and a procedure without it improvises at 3 AM.

`## Objective` is one or two sentences on what this produces and who it is for. Not the schedule, not the steps. An executor reads this to know whether it is on the right track.

`## Inputs and freshness` names the exact sources to read, the filters to apply, and a time window derived from the cadence. A daily scan reads the last day's data, not everything ever written; a weekly digest covers the last week. The window matches the cadence so each run sees exactly its own period and nothing from the previous one. A bounded read that finds nothing within that window is the no-result path, not a malfunction, so never page past the window or drop filters to manufacture a non-empty result.

`## Procedure` holds the steps, in order, in the imperative. Say what to do and, where a step could reasonably be done two ways, why this way. An executor that understands the reason handles the situation you did not anticipate; one following a rule blindly does not.

`## Output and delivery` gives the format and the destination, concretely enough to be checked. "A summary" is not a format. Name the sections, the ordering, the length, and where it goes.

`## Failure and no-result behavior` holds the four paths from step 4, written as the concrete instructions in that section's Good examples.

`## Done when` is the finish line, stated so a run can be graded against it. This is the acceptance criterion: the conditions under which the executor should finalize as success. Without it, a run that quietly did half the job finalizes green.

Write `## Failure and no-result behavior` and `## Done when` using the three closing verbs below — success, failed, skip — so the executor can match its situation to an ending without translating.

**Every run leaves its result in the run's own thread.** That thread is the audit record. A result sent only as a DM leaves it blank, and a finished run whose thread shows nothing reads to its owner as a run that never happened. Long output goes in a document; the thread carries the reference. Write the delivery section so this is what the executor does, not something it may do.

A run then ends with exactly one terminal verb, and each has a precondition it will not close without:

```bash
heliox automation run success <execution_id>   # the result is in the run's own thread, and every subscriber has been DM'd a digest
heliox automation run failed  <execution_id> --reason "<what broke>"      # the owner has been DM'd what broke; a thread mention does not count
heliox automation run skip    <execution_id> --reason "<checked what; why quiet>"  # a one-line all-clear in the thread, no digests
```

So "if there are no tickets, post 'No urgent tickets'" is the wrong shape for a no-result path: it describes a message, not an ending, and the run has no way to close. Write it as *skip with a reason recording what was checked*. Failure paths follow the same rule: write who gets told and which verb closes the run, not only what state it lands in.

### How to write it

Prefer the imperative, and explain the why. The reader is a capable model, not an interpreter. A step it understands the purpose of will be executed sensibly in circumstances you never imagined, while a step it can only obey literally will be obeyed literally in exactly the circumstance where that is wrong. Piling on capitalized MUSTs is a symptom of not having explained the reason.

Keep it as short as it can be while remaining unambiguous, because every run reads all of it. A section growing into reference material, like a long field mapping or a large list of source ids, belongs in a document the procedure points to rather than inline.

Keep evaluation cases, grades, and execution ids out of the procedure. The executor should receive only the instructions needed to do the work; the test evidence lives in the workspace from step 7 and is handed over separately in step 9.

### A complete example

```markdown
# Daily incident digest

## Objective
A short daily summary of new production incidents, posted for the ops team so
the morning standup starts from a shared picture.

## Inputs and freshness
Read #incidents for messages posted in the last 24 hours, filtered to those
tagged `sev1` or `sev2`. Twenty-four hours is the whole scope: this runs daily,
so anything older was covered by yesterday's digest.

## Procedure
1. Read the window described above.
2. Group the incidents by owning service. Grouping matters more than ordering,
   because the team reads this to see which service is having a bad week.
3. For each incident, capture: the service, one sentence on the impact, the
   current status, and a link to the originating message.

## Output and delivery
Post the digest in the run's own thread as a single message titled "Incidents,
<date>". One section per service, incidents as bullets under it. Keep the whole
message under 300 words; if there is more than that, summarize the long tail as
a count. Then DM the same digest to every subscriber. The thread copy is the
record; the DMs are the delivery, and `run success` will not close without both.

## Failure and no-result behavior
If no messages match the filter in the last 24 hours, post one line in the run's
own thread: "No new incidents since yesterday's report." Do not extend the
window or loosen the filter. A quiet period is a valid result, so close with
`heliox automation run skip <execution_id> --reason "checked #incidents for the
last 24h; no matching messages"`.

If #incidents cannot be read at all (permission error, connection error, 5xx),
wait 60 seconds and retry once. If the retry fails, post the failure in the run's
own thread ("Could not read #incidents: {error}"), DM the owner the same line,
then close with `heliox automation run failed <execution_id> --reason "Source
unreachable: {error}"`. The verb checks for both the thread record and the DM,
so a run that only DMs is rejected. Do not post a digest assembled from anything
but a successful read.

## Done when
The digest is in the run's own thread, every subscriber has received it, every
incident cited falls inside the 24-hour window, and the run is closed with
`heliox automation run success <execution_id>`.
```

## 6. Create it

### Pick the trigger

Choose the trigger type based on where the signal comes from, not on how the user phrased the request. Every request names a signal, and the signal is one of three things: a moment, a rhythm, or an event in another system. Decide which one it is before reaching for a flag.

**A moment that will pass — `--start` (one-shot).** The user names a deadline the work must land before: a meeting to prepare for, an invoice due Friday, a launch on the 14th. The date is known in advance and the automation's whole job is to hit it once. A one-shot is created enabled and fires exactly once at its start time; after that its slot is spent and cannot be re-armed — "the same reminder again" is a different moment and gets its own automation. If you find yourself creating the same one-shot again for each new instance (one per invoice, week after week), the signal was never a moment but a standing rule — build it once, as cron or an event trigger.

**A rhythm — `--cron` (recurring).** Time itself is the content boundary: a Monday digest exists to summarize the week since the last one, a morning brief covers yesterday. Nothing external decides when to run — the value is the regularity. A cron automation is created disabled and armed deliberately after the procedure is written, because a recurring trigger keeps firing forever.

**An event in another system — an event automation.** Something happens at a time nobody can predict — an issue is labeled urgent, a payment fails, a form is submitted — and the work is about that thing. Do not approximate it with cron: a cron that checks for events buys you delay (the event waits for the next tick), waste (most ticks find nothing), and a dedup problem (which events did the last tick already handle?) — three costs an event trigger simply does not have. Create it with NEITHER `--cron` nor `--start` — the three trigger kinds are mutually exclusive, and a schedule-backed automation cannot take an event trigger — then attach the trigger. When the source pushes a signed event, attach a webhook trigger: the source notifies Helio when something happens. When the source has no reliable push mechanism, attach a poll trigger: a lightweight check runs on a cron schedule and fires the automation only when it finds something worth acting on — the poll's cron decides when to check; the event decides whether to fire.

The most common misassignment is a rhythm phrase hiding an event signal. "Check every morning whether any ticket went urgent" names a cadence, but the signal is the urgent ticket, not the morning — built as an event trigger, the user hears about the ticket when it happens instead of reading a morning list of things that went urgent yesterday. The reverse also happens: "remind me before Thursday's review" is not a tiny cron — the review is a moment, so it is a one-shot. And a request you can complete right now is not an automation at all; do the work now instead of scheduling it.

"Checking every five minutes works fine" is a statement about acceptable delay, not a reason to poll instead of using a webhook. If the source supports webhooks, which you established in step 2, prefer them. They are fresher and avoid wasted checks.

Pass the source's stable delivery id as `fire_key`. It is the idempotency boundary that prevents duplicate runs on retries.

A poll handler is a classifier: every check ends in fire or don't-fire, and "worth acting on" has to be defined precisely enough to decide. Write the boundary cases down before writing the handler, and make the don't-fire cases *near misses*, meaning an event from the right source in the right shape that still should not wake an AI. An obviously irrelevant payload tests nothing.

For the full handler contract, signature verification, packaging, fixtures, deployment, and logging details, read [`references/event-triggers.md`](references/event-triggers.md).

### Create

Build the argument array as JSON and pass it through the args-file transport:

```json
["automation", "create", "<name>", "--cron", "0 9 * * 1-5", "--owner", "@<requester>",
 "--procedure", "# <name>\n\n## Objective\n<approved objective>\n\n## Procedure\n<approved steps>"]
```

```bash
heliox --json --args-file /absolute/path/create-automation.json
```

Use `--cron` (recurring), `--start` (one-shot), or neither (event automation — attach its trigger next); the kinds are mutually exclusive. When converting the user's phrasing to a cron expression: an explicit clock time is an exact cron ("every day at 9 AM" = `0 9 * * *`); vague wording ("every morning") gets a randomized minute offset so that all loosely-timed automations do not fire at the same second.

`--procedure` takes the markdown BODY, never a filename. The AI that executes this procedure days or weeks later cannot read a file path that existed on your runtime at creation time. Draft in a local file if it helps, but paste its contents into the argument JSON; the file serves only as `--args-file` transport.

After creating, confirm the procedure landed: `heliox document read <document_id>` should show the approved text, not an empty body or a file path. This is a storage check and nothing more. It proves the bytes arrived, not that they make sense to a stranger. That question is step 7's.

A `--cron` automation is created disabled, which is exactly what makes the next step safe: nothing fires on its own while you work. A `--start` one-shot is created ENABLED and will fire at its start time — it exists to hit a deadline, so creation arms it. If you intend to rehearse it first, disable it now (`heliox automation update <id> --enable false`) and re-enable it at handover; `references/evaluation.md` treats it as already live.

## 7. Run the scenarios

Step 3 proved that *you* could produce the output, with the whole conversation in your head. This step asks: does a fresh executor, reading only the procedure, reproduce it?

A run you fire here is a real run and closes like one: `success` once the result is in the run's own thread and every subscriber has a digest, `failed --reason` with the owner told what broke, `skip --reason` for a period that was genuinely quiet. Grade against that too. A scenario that produced the right text but left the thread empty, or finalized green while a delivery failed, is a failing scenario however good the output reads.

The mechanics live in [`references/evaluation.md`](references/evaluation.md): containment, the serial edit/fire/capture/restore loop, how to write expectations that can fail, how to grade, how to show results. Read it before your first fire. Three things are yours to decide, and they are below.

Two commands carry this step, and when you describe the work to the user, name them rather than describing the loop in the abstract. `heliox automation run <id>` fires it once while it stays disabled. `heliox automation run show <execution_id> --transcript --json` is how you read what happened, and the `--json` is not a preference: cards, approvals, and attachments have no plain-text form, so a run whose real output was a broken card renders as clean text without it. You would be grading the caption instead of the picture.

### Your scenarios are the paths from step 4

You already wrote them. `representative` is the path you walked in step 3, and the four you only imagined are `no-result`, `step-fails`, `partial`, and `source-down`. Step 4 asked you to write them specifically enough to check. This is the checking.

Firing all five for a Friday reminder is waste; firing only the representative one for a Stripe automation is negligence. The blast radius from question 4 decides it. Recommend a tier in one sentence with a reason, and let the user adjust:

| The automation | Fire these |
| --- | --- |
| Deterministic, no external side effect (a reminder, a fixed-text nudge) | `representative` only |
| Reads varying data, silence is meaningful (a digest, a scan) | `representative` + `no-result` |
| Has an outward or irreversible effect (mail, payment, external write), or reads three-plus sources | the full set + `baseline` |

### Your inputs come from moving the window, not from waiting

The procedure names a time window, so you change the input by changing the window. You are not waiting for next Monday; you are reading last Monday. Three real windows read today beat one real window read three weeks from now.

For `representative`, use a real recent window with data in it, preferring the most recent complete period.

For `no-result`, use a real window you have already verified is empty, or the same read narrowed to an hour you know was quiet. Real emptiness, not a pretend one: the point is to see what the executor does when the source honestly has nothing.

For `step-fails`, `partial`, and `source-down`, inject the fault, because you cannot wait for GitHub to break. Point one source at an unreachable address, or at a channel the executor has no access to.

### Your baseline is the user's original sentence

Fire the automation once with the procedure body replaced by the one-line request the user opened with. Keep every containment substitution in place: retargeted destinations, scratch channels, modified subscriber lists. The baseline isolates one variable, the procedure's guidance, and containment is not part of that variable. A baseline that reverts the containment fires at the real destination, which defeats the loop.

If the procedure's outward effects cannot be contained, because retargeting is impossible or the only safe target is the real one, do not fire a baseline. Note the gap in the results and move on. The approved output from step 3 remains the only evidence for that path, and step 9's handover must say so.

If the baseline produces roughly the same output, most of the procedure is not earning its place and can be cut. If the baseline drifts, using the wrong window or the wrong format, or inventing a summary when there was nothing to summarize, you now know exactly which parts are load-bearing and you will not delete them by accident in step 8.

### Record what the rehearsal taught you

The loop ends by writing what it taught into the automation's experience record —
which paths held, which are still unproven, what a scenario made you change, and
what the sources actually do rather than what their docs claim. The full list,
and why the pass rate is not part of it, is in
[`references/evaluation.md`](references/evaluation.md).

For a new automation this is its FIRST entry, and step 9 hands that record to the
owner. Skip it and you hand over an empty one: everything this rehearsal learned
leaves with your context, and the refiner inherits nothing to reason from.

## 8. Improve until it holds

You are iterating on two or three windows of data, and the automation will run on hundreds. The replay mechanics and the stop conditions are in [`references/evaluation.md`](references/evaluation.md); what follows is how to decide *what to change*.

Generalize rather than tuning to the window. The failure you just watched is an instance of something. Fix the smallest general defect that covers it, not the instance. A procedure that handles last Tuesday because you wrote last Tuesday into it has learned nothing.

Cut what is not earning its place. Read the transcripts, not just the outputs. If the executor spent four tool calls doing something the digest did not need, find the sentence that sent it there and delete it. The baseline run tells you which parts are load-bearing; everything else is a candidate.

Explain rather than command. When a run misreads a step, the reflex is to make the step louder. Try making it clearer first: say why the step exists, and the executor will handle the neighbouring case you have not tested. Capitalized MUSTs are what you reach for when the explanation is missing.

Put recurring work somewhere durable. If every run re-derives the same query, mapping, or format, pin it down: in the procedure if it is short, in a document the procedure points at if it is long, in the trigger handler if it is really a decision about whether to run at all.

## 9. Hand it over

Restore the real configuration first. Undo each scenario variant with the inverse `heliox document edit`, using the `--old` and `--new` strings you recorded when you made it, and put the real destinations and subscribers back. Then confirm what is actually stored rather than what you meant to store, with `heliox document read <document_id>` and `heliox automation subscriber list <id>`. A scratch channel left in the delivery step is the single most likely way this automation ships broken, and it will look fine right up until the first real fire.

Then tell the user what now exists:

- The automation id and its name
- How it triggers (schedule, webhook, or poll) and the cadence or event
- Where results go and who receives them
- What it can do on its own: the blast radius from question 4, in plain terms. If it emails people outside the company, writes to a shared system, or moves money, say so here, in a sentence, without hedging. This is the last moment before it can act unattended.
- Which scenarios were run and what held, with the workspace path so the evidence is findable later
- Which paths from step 4 are still unproven
- Its live state. A `--cron` automation is still disabled: nothing has fired on its own and nothing will until it is turned on — write out the exact command that turns it on, `heliox automation update <id> --enable true`, with the real id filled in. A `--start` one-shot is enabled — say plainly when it will fire. If you disabled it to rehearse, re-enable it ONLY while its start is still in the future: enabling a one-shot whose start has passed fires it immediately, turning the rehearsal into a late production run. Past the deadline, ask for a new time or explicit confirmation instead.

Do not drop or soften that bullet. A recurring automation the user cannot start is not delivered — "let me know when you want it enabled" names no command; the written-out command does. An armed one-shot must be named as armed: this is the last moment before it acts unattended.

Do not enable a recurring automation until the user says to. When they say "turn it on," do it, then tell them it is live and when it will first fire.

The automation carries a directory, not just its procedure. Two files in it
matter to the owner from day one. **experience.md** already has the rehearsal
entry you wrote in step 7 — show it to them, so they can see what this thing
learned about itself before it ever ran unattended. **feedback.md** is theirs:
what they put there is what every later refinement round treats as the target,
and only they can write it. Point them at it by name.

From here on, the automation belongs to `heliox:automation-refiner`, which repairs it when it decays, changes what it produces, and reviews how it has been running. Point the user there.

## When the loop does not run

Two different things stop step 7 from happening, and they call for opposite responses. Sort out which one you are in before you write anything.

### You have been asked to hold off

The user says "describe it first", "don't create anything yet", "just tell me what you'd do", or you are in an environment that forbids side effects. Nothing is blocked; you have been asked not to act yet.

Describe the whole loop as you would run it, in the same detail you would use to actually run it. Name the tier you would pick and why. Name the window you would move the read to for the representative input, and the window you would use for the no-result one. Name what you would use as the baseline. The user is deciding whether to let you proceed, and a plan that omits the part they are approving is not a plan they can approve.

Do not describe this situation as a limitation, and do not list the steps you are "unable" to do. You are able to do them; you have been asked to wait. Saying otherwise reads as an excuse for a thinner answer, and it is the most common way this step goes wrong.

### You tried and the run is not available

Something outside your control stops the run. Say which case you hit and what it costs. Do not quietly skip to handover and present an untested automation as a finished one.

The source may have no usable historical window, because it only updates on weekdays and today is Sunday, or because the API has no date filter. Run what you can, and hand over naming the scenario you could not produce.

The procedure's side effects may not be containable, because it can only write to the real destination. Do not fire it. Fall back to the approved output from step 3 as the only evidence, and tell the user plainly that no end-to-end run has happened.

The automation may be triggered by an external event (webhook, poll) whose payload the rehearsal cannot reproduce. A manual run wakes the executor with no event context, so when the procedure reads data from the triggering event, the rehearsal is not representative. Fall back to the approved output from step 3 as the only evidence, and tell the user plainly that the event-bearing rehearsal path is not available.

The automation may already be enabled, because the user turned it on mid-conversation. Stop and switch to `heliox:automation-refiner`. From that point on the next scheduled run delivers to real subscribers, and that is its loop, not this one.

## Output language

- Name, description, and procedure follow the user's own instruction language, not a wrapper sentence around it. A mixed-language instruction follows its dominant language.
- If the instruction is too short to tell (a one-line edit), fall back to the language the conversation is in.
- This applies to artifacts only. Conversational replies stay in the conversation's language, so the two can differ.

## Boundaries

A procedure is a maintained document, not a program. It describes what to do in prose that an AI executor reads and follows. If you find yourself writing conditional logic, loops, or branching control flow inside the procedure, the logic belongs somewhere that can execute it: a decision about *whether to run at all* goes in the poll handler (see step 6), and a computation the run needs goes in a script the procedure points at. Leaving it in the procedure means re-deriving it, slightly differently, on every run.

This skill runs while the conversation that started the automation is still
going. Its steps depend on things that live in that conversation: the approved
output from step 3, the paths written down in step 4, the workspace holding the
evidence. If a user comes back in a later conversation about an automation
built in an earlier one, those are gone even when the automation was never
enabled, so that request belongs to `heliox:automation-refiner`, whose way of
finding evidence does not depend on them. Being unenabled is not what puts an
automation in this skill's hands; being mid-creation is.

One automation is one coherent job. If the user asks for two different things on two different schedules, those are two automations, not one automation with internal branching.

---

Put these nine steps in your working list before you start, so that steps 7 and 8, the ones that turn predictions into evidence, do not get skipped:

1. Pin down what they want
2. Check the ground
3. Do the work once, here
4. Write down the paths you did not see
5. Write the procedure
6. Create it
7. Run the scenarios
8. Improve until it holds
9. Hand it over
