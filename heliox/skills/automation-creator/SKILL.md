---
name: automation-creator
description: "Create a Helio automation for AI work that should run later. Use when the user asks for a reminder, a recurring report or digest, wants you to watch or monitor something, notify people when an event happens, or follow up later, even if they never say automation. Infer Scheduled, Pushed, or Observed privately. Do not use for a one-off task now, a human calendar event, or an SOP with no future AI run. Send any automation from a prior conversation to automation-refiner, whether or not it was enabled. If the request includes an automation-rec-*.zip screen-recording package, use automation-recorder instead."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox automation --help"
---

# Heliox Automation Creator

First, decide what is in front of you:

- A new automation taking shape in this conversation: this skill, steps 1 to 9 below.
- Any automation from an earlier conversation, enabled or not: `heliox:automation-refiner`.
- Work to finish once, now, a human calendar entry, or an SOP with no future AI run: not an automation; do the work or write the document instead.
- An `automation-rec-*.zip` screen-recording package: `heliox:automation-recorder`.

This skill turns a request into an automation: a trigger, a procedure document, and an AI that executes it. Before handover, run cron, event, and catalog automations against real data. Do not manually run a one-shot because that would do a once-only job twice. Validate it with the output the user approved in this conversation, source and access checks, and the stored procedure read-back. Everything after an automation goes live belongs to `heliox:automation-refiner`, which repairs it when it decays, changes what it produces, and reviews how it has been running.

The user supplies the outcome, not the architecture. A short request such as "keep an eye on our important orders" is normal input. Research the source, choose how to observe it, write any trigger code, and test it yourself. Do not turn implementation choices into a questionnaire for the user.

Creating an automation goes like this: follow sections 1 through 9 below. Do not stop at creation. Steps 7 and 8 test whether a fresh executor can repeat the work without this conversation. Skip both for a one-shot so the job does not run twice.

Work out where the user already is before you start. Three common openings:

1. Nothing exists yet. Start at step 1. This is the default path.
2. The user brought an approved example, pasted or described. Step 3 is already done; align on any gaps, then move to step 4.
3. A built-in template fits. `heliox automation catalog list` / `show <id>` holds proven recurring procedures such as daily priorities, weekly reflection, and inbox triage. Check it before writing from scratch. If you notice a recurring need nobody has named, offer the matching template in one sentence: what would run, when, and what they would receive. Install only after they agree: `heliox automation catalog install <id> --timezone <owner IANA timezone> --idempotency-key <stable-approved-install-key> --json`, and reuse the exact key on every retry. The install leaves the automation disabled while its first run executes; enable it only after that run finishes safely. Do not copy its procedure into a generic `automation create`; installation preserves the template binding a managed provider flow may require.

## Talking to the user

Assume the user is not technical unless they show otherwise. Talk about what you will watch, when you will tell them, and what the teammate will do. Do not ask them to choose a cron, webhook, poll interval, API endpoint, cursor, fire key, or credential storage method. Those are your implementation decisions.

Keep two layers separate:

- **Private build plan:** source research, trigger choice, signatures, credentials, stable identity, retry behavior, procedure, rehearsal fixtures, and evidence.
- **User conversation:** the outcome they will experience, safe defaults, the one business choice you still need, and whether anything has been created or turned on.

Keep replies at decision points to five short sentences or fewer. Confirm the outcome, explain when it will stay quiet, state any important default, and ask at most one business question. Do not paste a procedure, implementation plan, test matrix, failure table, or sample payload unless the user asks for technical detail. "Describe the plan" still means a plain-language product plan.

Ask only about a business choice that changes the result. Translate it into a
question they can answer:

- "Should I include things that are already there, or only new ones from now on?"
- "Should I tell you once when it becomes a problem, or keep reminding you while it stays that way?"
- "Is hearing about it within about five minutes fast enough?"

If the request could mean either "check once now" or "keep watching", do the one-off work now. When continued monitoring would clearly help, offer it in one sentence: "I can also keep an eye on this and only tell you when something changes." Create nothing recurring until the user agrees. "Keep watching" or "tell me when" already expresses that agreement; do not ask again.

Some of the vocabulary below is yours, not theirs.

Always translate the words below. They are internal names for things the user already understands:

| You say to the CLI | You say to the user |
| --- | --- |
| procedure | the steps |
| executor | who runs it |
| subscriber | who gets the results |
| disabled | not turned on yet |

Introduce these only if the user reaches for them first: cron expression, webhook, poll, API, signature, cursor, fire key, idempotency, deduplication, subscriber snapshot, backtest, fixture, run record. They are precise and worth using once they are on the table, but leading with them turns a conversation into a form. The same rule applies to unsolicited explanations: do not say "I chose a webhook" merely because you did not ask the user to choose it.

The rest is register. "Every weekday at 8:30" needs no translation; `30 8 * * 1-5` does. Say what you did in their terms and keep the expression to yourself unless they ask to see it. If they open with "set up a cron for", match them.

## 1. Pin down what they want

First decide whether this is an automation at all. It is when a future time or outside change should wake an AI to do work. "Keep an eye on this," "tell me when," and "send this every week" are enough. A task to finish only now, a human calendar entry, a document that merely describes an SOP, or work on an automation from an earlier conversation belongs elsewhere.

Read the conversation before asking anything. A common request is "that thing you just did, do it every week." In that case, the tools, corrections, and approved output already describe the job. Summarize what you learned and ask only for what is missing. Repeating questions the user already answered makes it look as if you did not listen.

Four answers drive the rest of the process. Infer them from the conversation, the source, and the defaults below. Ask only for an answer that remains genuinely ambiguous, one natural question at a time rather than as a form:

1. What should this automation produce? A summary, a status report, a notification, a document. This sets the shape of the procedure and the output format.
2. What makes it run? Ask for the occasion, not a cron expression: "every Monday morning before standup" or "whenever a new issue is labeled urgent." Converting that into a cron string or a webhook filter is your job, not the user's.
3. What does the result look like, and who receives it? This determines the output section of the procedure and whether you need subscribers.
4. What happens if it gets this wrong while nobody is watching? A reminder posted into a private chat is worth one answer; an email to a customer, a payment, or a public post is worth another. You are asking for the blast radius, and it is load-bearing twice over: it sets how hard you test in step 7, and it is the thing you must name out loud at handover in step 9.

Use sensible defaults and ask only about what remains. Results go to the current conversation. The server assigns ownership to your human owner; anyone else who wants to own an automation creates their own. You are the executor. Only the owner receives successful results and failure notices unless they add subscribers. Quiet runs notify nobody.

Do not create anything until all four questions have answers; an answer can be a safe default rather than another question. This runs unattended and repeatedly, so a half-understood request becomes a half-correct procedure.

## 2. Check the ground

Go look at the things this automation depends on before you commit to anything about them. Run these checks yourself rather than asking the user to translate their need into system details. If they name a product rather than an API, discover the official integration, API, and event surface yourself. Keep the source URL and version or retrieval date in the private build evidence. Ask for an endpoint or documentation only when the source is genuinely private or custom and you cannot discover it; never invent a contract to keep moving.

Is the source actually reachable, and does it return what everyone assumes it returns? Read it once. A channel that was renamed, an endpoint that moved, or a report that no longer has the column the user described is cheaper to find now than in step 3.

Which way does the signal travel? A connected account proves that the executor can use its API; it does not prove Helio can subscribe to its events. Treat a source as pushed only when a current Helio managed flow can bind this automation, or when you can register Helio's callback in the source and prove a test delivery. If Helio must read the source's API to notice change, it is observed. Provider documentation that merely says "webhooks supported" is not enough. For either event path, read [`references/event-triggers.md`](references/event-triggers.md) and complete its private trigger contract before promising reliable recognition.

Will the executor be able to do this? You are about to do the work yourself, in this conversation, with the tools and credentials *you* have connected right now. The automation will run later as the executor. If those are not the same identity, or the executor lacks an integration or a vault credential you are about to use, the run in step 7 is where you find out, unless you check here. Name the specific access needed and get it arranged rather than designing around a gap you have not confirmed.

Does the destination exist? The channel, document, or address the results go to.

Does one of these already run? `heliox automation list --json` before you create a recurring one. A second automation covering the same ground is worse than none: both fire, the owner gets two digests that disagree, and neither is obviously the stale one. If something close already exists, refine it (`heliox:automation-refiner`) instead of adding a rival.

Come to the user with this already done; every skipped check becomes their question or their failure.

## 3. Do the work once, here

At creation time you have zero run data. A real output exposes preferences, format issues, and missing context faster than any questionnaire.

Before you execute anything, look at the blast radius from question 4. If the work has an outward or irreversible effect, sending mail, filing a ticket, posting somewhere public, moving money, then doing it "once, here" is doing it for real, to real people, before any of the containment in step 7 exists. Point that step at yourself or a scratch destination first, exactly as step 7 will, or ask the user to approve this single live execution and say plainly what it will do. Do not perform it unannounced because the request happened to be executable.

With that settled, execute the request once in the current conversation. If the real event cannot be produced right now (the source only updates on weekdays, say), use a clearly labeled historical example and tell the user it is historical.

Show the output to the user and get their sign-off. This output is the standard everything later is measured against: step 7 asks whether a fresh executor, reading only the procedure, reproduces it.

Pay attention to what they change. Their corrections are the real specification, but each correction is about this one output while you are writing something that runs forever, so ask which it is. "Drop the Bugs column" might mean *this week's bugs column was empty* or *never show bugs*. Those produce different procedures, and only one of them is right.

Bad:
> The user removed the "Blocked" section from the draft, so the procedure says: "Do not include a Blocked section."

Good:
> The user removed the "Blocked" section from the draft. Asked whether to drop it always or only when empty; they said only when empty. The procedure says: "Include a Blocked section only when at least one item is blocked; omit the heading entirely otherwise."

If the user brought an approved example or has an existing automation to work from, start there instead of redoing the work.

## 4. Write down the paths you did not see

Step 3 exercised one path: everything worked and data was available. Every procedure also needs explicit handling for the four situations below. They double as step 7's test cases, so write each one specifically enough to check whether a run obeyed it.

### Nothing found

A bounded read that returns no results within the time window is a normal outcome, "nothing happened this period". It is not an error, and not a reason to widen the search. The procedure should spell out what "nothing found" looks like and what to report.

Bad:
> "If no results are found, try expanding the search window or removing filters."

Good:
> "If no messages match the filter in the last 24 hours, post a one-line summary in the run's own thread: 'No new incidents since yesterday's report.' Do not extend the window or loosen the filter. A quiet period is a valid result, so close with `heliox automation run skip <execution_id> --reason \"checked #incidents for the last 24h; no matching messages\"`."

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

Work through these paths privately using the safest reversible defaults. Ask the user only when the choice materially changes what they receive or what the automation can do to other people or systems. Phrase that one question as an ordinary consequence: "If one source is temporarily unavailable, would you rather receive the partial brief with a warning, or wait for the complete one?" Do not walk a novice through an error-handling questionnaire.

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

Every section is required. `## Objective` is one or two sentences on what this produces and who it is for. Not the schedule, not the steps. An executor reads this to know whether it is on the right track.

`## Inputs and freshness` names the exact sources to read, the filters to apply, and a time window derived from the cadence. A daily scan reads the last day's data, not everything ever written; a weekly digest covers the last week. The window matches the cadence so each run sees exactly its own period and nothing from the previous one. A bounded read that finds nothing within that window is the no-result path, not a malfunction, so never page past the window or drop filters to manufacture a non-empty result.

`## Procedure` holds the steps, in order, in the imperative. Say what to do and, where a step could reasonably be done two ways, why this way. An executor that understands the reason handles the situation you did not anticipate; one following a rule blindly does not.

`## Output and delivery` gives the format and the destination, concretely enough to be checked. "A summary" is not a format. Name the sections, the ordering, the length, and where it goes.

`## Failure and no-result behavior` holds the four paths from step 4, written as the concrete instructions in that section's Good examples. Without it the unwatched runs improvise.

`## Done when` is the finish line, stated so a run can be graded against it. This is the acceptance criterion: the conditions under which the executor should finalize as success. Without it, a run that quietly did half the job finalizes green.

Write `## Failure and no-result behavior` and `## Done when` using the three closing verbs below: success, failed, and skip. This lets the executor match its situation to an ending without translating.

**Every run leaves its result in the run's own thread.** That thread is the audit record. A result sent only as a DM leaves it blank, and a finished run whose thread shows nothing reads to its owner as a run that never happened. Long output goes in a document; the thread carries the reference. Write the delivery section so this is what the executor does, not something it may do.

A run ends with exactly one terminal verb, and each has a precondition:

```bash
heliox automation run success <execution_id>   # the result is in the run's own thread, and every subscriber was reached (a DM digest or a feed push both count)
heliox automation run failed  <execution_id> --reason "<what broke>"      # the owner has been DM'd what broke; a thread mention does not count
heliox automation run skip    <execution_id> --reason "<checked what; why quiet>"  # a one-line all-clear in the thread, no digests
```

So "if there are no tickets, post 'No urgent tickets'" is the wrong shape for a no-result path: it describes a message, not an ending, and the run has no way to close. Write it as *skip with a reason recording what was checked*. Failure paths follow the same rule: write who gets told and which verb closes the run, not only what state it lands in.

### How to write it

Prefer the imperative, and explain the why: a step whose purpose the executor understands is handled sensibly in circumstances you never imagined. Capitalized MUSTs are a symptom of a missing reason.

Keep it as short as it can be while remaining unambiguous, because every run reads all of it. A section growing into reference material, like a long field mapping or a large list of source ids, belongs in a document the procedure points to rather than inline. Keep evaluation cases, grades, and execution ids out too: the executor should receive only the instructions needed to do the work, and the test evidence is handed over separately in step 9.

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
record; the DMs are the delivery.

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
unreachable: {error}"`. Do not post a digest assembled from anything but a
successful read.

## Done when
The digest is in the run's own thread, every subscriber has received it, every
incident cited falls inside the 24-hour window, and the run is closed with
`heliox automation run success <execution_id>`.
```

## 6. Create it

### Pick the trigger

Choose from the user's intended experience, not from technical words they may or may not know. First decide what starts the work:

**Scheduled.** A known time or repeating rhythm starts the work. Use `--start` for one known moment, such as preparing before Friday's meeting. A one-shot is created enabled, fires once, and cannot be re-armed. Use `--cron` when each period deserves a run, such as a Monday digest or nightly reconciliation. A cron automation is created disabled and armed after rehearsal.

**Pushed.** Another system calls Helio when something happens. Use a current managed provider flow only when it can bind this exact automation. For a generic provider or a custom caller, create an event-only parent and attach `--kind webhook`. Choose this only when you can authenticate the delivery, configure the Helio URL in the source, and prove a source-originated test delivery. An existing connection, or a provider that supports webhooks in theory, does not meet that bar. There is no `--kind api`; a custom system that POSTs to Helio is still a webhook.

**Observed.** Helio must call an external read API to notice change. Create an event-only parent and attach `--kind poll`. Its clock only decides when cheap code checks; a stable source event, revision, or explicit reminder bucket decides whether the AI wakes. Do not call this pushed merely because the API belongs to a connected product.

Use direction to classify API-based requests: source to Helio is Pushed; Helio to source is Observed. Watch for time words that hide an event: "check every morning whether a ticket went urgent" is Observed if the user only wants to hear about new urgent tickets, and Scheduled if they want the morning report even when nothing changed. "Remind me before Thursday's review" is a one-shot. Work that can be completed now is not an automation. Ask only when the intended experience is unclear.

Before writing event code, decide the match, beginning, stable identity, repeat behavior, and event context. Use a stable delivery ID as `fire_key` for pushed events. If a business choice remains, translate only that choice into plain language and ask it. For source research, the trigger contract, code templates, credentials, idempotency, and local fixtures, follow [`references/event-triggers.md`](references/event-triggers.md). Keep all of that work invisible unless the user asks how it was built.

### Create

Do not create until you have read authoritative documentation AND made one representative source call for every external source; a documentation link returned by provider help is discovery, not a read. Then build the argument array as JSON and pass it through the args-file transport:

If a catalog template is the chosen path, use `automation catalog install` after the user's explicit agreement and skip the generic create command below. Capture the returned automation and first-run coordinates, wait for that run to finalize, inspect it with `automation run show`, and enable the automation only when the result is safe. If the run did not start or its result is unsafe, leave it disabled and report the concrete blocker.

```json
["automation", "create", "<name>", "--cron", "0 9 * * 1-5",
 "--creation-source", "chat",
 "--idempotency-key", "<stable-key-for-this-approved-create>",
 "--procedure", "# <name>\n\n## Objective\n<approved objective>\n\n## Procedure\n<approved steps>"]
```

```bash
heliox --json --args-file /absolute/path/create-automation.json
```

Mint one `--idempotency-key` per approved create and reuse the exact key on
every retry of it. A fresh key per retry can create duplicates.

Use `--cron` (recurring), `--start` (one-shot), or neither (event automation; attach a `webhook` or `poll` trigger next). These choices are mutually exclusive, and `api` is not a trigger kind. When converting the user's phrasing to a cron expression, an explicit clock time is exact ("every day at 9 AM" = `0 9 * * *`); vague wording ("every morning") gets a randomized minute offset.

`--procedure` takes the markdown BODY, never a filename. The AI that executes this procedure days or weeks later cannot read a file path that existed on your runtime at creation time. Draft in a local file if it helps, but paste its contents into the argument JSON; the file serves only as `--args-file` transport.

After creating, confirm the procedure landed: `heliox document read <document_id>` should show the approved text, not an empty body or a file path. This is a storage check and nothing more. It proves the bytes arrived, not that they make sense to a stranger. That question is step 7's.

Each shape is created in a different state, and the state decides what you do next:

- **Cron**: created disabled. Rehearse it in step 7; arming happens at handover.
- **Event-only**: starts disabled too. Finish the contained procedure rehearsal and local handler tests while it is off. Enable the parent only for the source-originated proof, because an event handler cannot fetch its bound credential or fire while the parent is disabled. After that proof, keep it enabled only when the user authorized ongoing operation and every required path held; otherwise disable it immediately.
- **One-shot**: created enabled, fires once at its start time. Never rehearse or manually run a one-shot: a manual run performs the real job once, so rehearsal would turn a single requested execution into two. Its evidence is the approved output from step 3, source and access checks, and the stored procedure read-back. Disable it only when the user named other recipients and its scheduled time leaves enough room: the owner must add them before its only run fires, or they will miss it.

## 7. Run the scenarios

Step 3 proved that *you* could produce the output, with the whole conversation in your head. This step asks: does a fresh executor, reading only the procedure, reproduce it?

Skip this entire step for a `--start` one-shot. Do not call `heliox automation run` and do not create a baseline run. That command is another real execution, not a preview. Record that the one-shot was validated from the approved step 3 output, the source and access checks, and the canonical procedure read-back, then continue to handover. Steps 7 and 8 apply to cron, event, and catalog automations.

Fire every scenario as a rehearsal: `heliox automation run <id> --rehearsal --fire-key <scenario>:<n>`. A rehearsal executes for real and closes with the same terminal verbs. Its failures stay out of the consecutive-failure auto-disable count, and `success` closes without requiring subscriber digests. Fire keys are durable per automation: a reused key returns that finished run instead of firing again, so mint a fresh key for every new fire and reuse one only to retry that same fire. Grade the ending too. A scenario that produced the right text but left the thread empty is a failing scenario, however good the output reads.

Read [`references/evaluation.md`](references/evaluation.md) before the first fire. It covers containment, the edit/fire/capture/restore loop, expectations, grading, and results. The choices that remain are below. Read each fire back with `heliox automation run show <execution_id> --transcript --json`, where `--json` is required: cards, approvals, and attachments have no plain-text form, so without it a broken card renders as clean text and you grade the caption instead of the picture.

### Run the paths from step 4

You already wrote them. `representative` is the path you walked in step 3, and the four you only imagined are `no-result`, `step-fails`, `partial`, and `source-down`. Step 4 asked you to write them specifically enough to check. This is the checking.

Firing all five for a Friday reminder is waste; firing only the representative one for a Stripe automation is negligence. The blast radius from question 4 decides it. Recommend a tier in one sentence with a reason, and let the user adjust:

| The automation | Fire these |
| --- | --- |
| Deterministic, no external side effect (a reminder, a fixed-text nudge) | `representative` only |
| Reads varying data, silence is meaningful (a digest, a scan) | `representative` + `no-result` |
| Has an outward or irreversible effect (mail, payment, external write), or reads three-plus sources | the full set + `baseline` |

### Move the window instead of waiting

The procedure names a time window, so you change the input by changing the window. You are not waiting for next Monday; you are reading last Monday. Three real windows read today beat one real window read three weeks from now.

For `representative`, use a real recent window with data in it, preferring the most recent complete period.

For `no-result`, use a real window you have already verified is empty, or the same read narrowed to an hour you know was quiet. Real emptiness, not a pretend one: the point is to see what the executor does when the source honestly has nothing.

For `step-fails`, `partial`, and `source-down`, inject the fault, because you cannot wait for GitHub to break. Point one source at an unreachable address, or at a channel the executor has no access to.

### Fire a baseline from the user's original sentence

Fire the automation once with the procedure body replaced by the one-line request the user opened with. Keep every containment substitution in place: retargeted destinations, scratch channels, the audience still unattached. The baseline isolates one variable, the procedure's guidance, and containment is not part of that variable. A baseline that reverts the containment fires at the real destination, which defeats the loop.

If the procedure's outward effects cannot be contained, because retargeting is impossible or the only safe target is the real one, do not fire a baseline. Note the gap in the results and move on. The approved output from step 3 remains the only evidence for that path, and step 9's handover must say so.

If the baseline produces roughly the same output, most of the procedure is not earning its place and can be cut. If the baseline drifts, using the wrong window or the wrong format, or inventing a summary when there was nothing to summarize, you now know exactly which parts are load-bearing and you will not delete them by accident in step 8.

### Record what the rehearsal taught you

The loop ends by writing what it taught into the automation's experience record: which paths held, which are still unproven, what a scenario made you change, and what the sources actually do rather than what their docs claim. The full list, and why the pass rate is not part of it, is in [`references/evaluation.md`](references/evaluation.md).

For a rehearsed cron, event, or catalog automation, this is its FIRST entry, and step 9 hands that record to the owner. Skip it and you hand over an empty one: everything this rehearsal learned leaves with your context, and the refiner inherits nothing to reason from. A one-shot records the validation evidence named above instead.

## 8. Improve until it holds

You are iterating on two or three windows of data, and the automation will run on hundreds. The replay mechanics and the stop conditions are in [`references/evaluation.md`](references/evaluation.md); what follows is how to decide *what to change*.

Generalize rather than tuning to the window. The failure you just watched is an instance of something. Fix the smallest general defect that covers it, not the instance. A procedure that handles last Tuesday because you wrote last Tuesday into it has learned nothing.

Cut what is not earning its place. Read the transcripts, not just the outputs. If the executor spent four tool calls doing something the digest did not need, find the sentence that sent it there and delete it. The baseline run tells you which parts are load-bearing; everything else is a candidate.

Explain rather than command. When a run misreads a step, the reflex is to make the step louder. Try making it clearer first: say why the step exists, and the executor will handle the neighbouring case you have not tested. Capitalized MUSTs are what you reach for when the explanation is missing.

Put recurring work somewhere durable. If every run re-derives the same query, mapping, or format, pin it down: in the procedure if it is short, in a document the procedure points at if it is long, in the trigger handler if it is really a decision about whether to run at all.

## 9. Hand it over

Restore the real configuration first. Undo each scenario variant with the inverse `heliox document edit`, using the `--old` and `--new` strings you recorded when you made it, and put the real destinations back. Then confirm what is actually stored, not what you meant to store: `heliox document read <document_id>` and `heliox automation subscriber list <id>`. A scratch channel left in the delivery step is the single most likely way this automation ships broken, and it looks fine right up until the first real fire. The audience is the one piece you cannot restore yourself: subscriber changes are owner-only, so recipients beyond the owner are named in the handover below for the owner to add.

Then tell the user what now exists:

- Its name, what it will notice, how soon it will respond, and where the result
  will go, all in the user's words.
- What it may do without asking again. Name outward messages, shared-system
  writes, or money movement plainly.
- What you proved and any important path that remains unproven.
- Its real live state, by shape:
  - "Send this every day from now on" or another clear request for future runs
    already approves a proven schedule; do not ask twice.
  - A one-shot stays armed unless it was paused so the owner could add
    recipients; arm it again only after the audience is complete and before
    its deadline.
  - An event automation stays off through authoring, local handler tests, and
    manual procedure rehearsal. Once registration is ready, turn it on for a
    contained source delivery proof, then retain or restore the live state
    the user authorized.
  - Keep any automation off when the user asked to wait, rehearsal did not
    establish safe operation, its audience is incomplete, or a high-risk
    business choice remains unresolved.

For a non-technical user, fit that handover into five short sentences. Do not
send the automation id, a CLI command, workspace paths, test counts, trigger
jargon, or credential details. Those belong in captured state and the
experience record. End with the action they can actually take in the
conversation when it is off: "Reply 'start' and I'll turn it on." If they have used
technical language or ask for the implementation, give the id, exact enable
command, evidence paths, and trigger details in a separate technical reply.

Do not infer approval from interest or a proposal. When the user has clearly
asked for future runs, enable the proven automation yourself and say when it
starts. Arming what you execute is your own act:
`heliox automation update <id> --enable true` on its own, with nothing else in
the call. [`references/your-authority.md`](references/your-authority.md) has
the rest of what an executor holds, and what does belong to someone else.

For cron, event, and catalog automations, the experience record already contains the rehearsal entry from step 7. For a one-shot, record only the validation evidence from step 3 and the storage read-back; do not imply that a manual run occurred. The owner can write feedback for future refinements. Keep both records, but do not make a novice learn their filenames. If they later ask to change the result or say it stopped working, use `heliox:automation-refiner` without asking them to choose a skill.

## When the loop does not run

Two different things stop step 7 from happening, and they call for opposite responses. Sort out which one you are in before you write anything.

### You have been asked to hold off

The user says "describe it first", "don't create anything yet", "just tell me what you'd do", or you are in an environment that forbids side effects. Nothing is blocked; you have been asked not to act yet.

Give the user the product plan, not the build transcript. In no more than five
short sentences, say what will be watched, what will make them hear from it,
what will stay quiet, which important action it will never take on its own, and
the one business answer still needed. Say that you will verify it with a real
example before turning it on, but keep the trigger mechanics, procedure body,
test tier, historical windows, fixtures, baseline, retry policy, and run-state
verbs in your private working plan. If the user explicitly asks for the
technical design or test plan, then show the relevant layer.

Do not describe this situation as a limitation, and do not list the steps you are "unable" to do. You are able to do them; you have been asked to wait. Saying otherwise reads as an excuse for a thinner answer.

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

One automation is one coherent job. If the user asks for two different things on two different schedules, create two automations instead of putting branches inside one.
