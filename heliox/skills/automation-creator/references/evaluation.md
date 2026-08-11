# The automation evaluation loop

Read this when you are about to prove an automation does what it should,
either the first time it is built (`heliox:automation-creator` step 7) or after
a change to one that already exists (`heliox:automation-refiner` step 5). The
mechanics below are the same either way.

Three things are not defined here, because they are exactly what differs
between the two cases. The skill that sent you here defines them:

- what your scenarios are, meaning the situations worth running;
- where their inputs come from, whether real windows, narrowed windows, or
  injected faults;
- what counts as your baseline, meaning the thing the candidate is compared to.

## Before the first fire

Check these; do not assume them.

The automation must be disabled. `heliox automation create` leaves a `--cron`
automation that way; a `--start` one-shot is created ENABLED and will fire at
its start time — treat it as already live.
For one that is already live, disable it before a meaningful behavioral change:
`heliox automation update <id> --enable false`. Disabling is what stops the
schedule from firing underneath you while you work. Record that it was live:
at handover, tell the user the automation was disabled for testing and offer to
re-enable it with `heliox automation update <id> --enable true`.

You must know who is subscribed. `heliox automation subscriber list <id>` shows
the effective audience, owner included. The owner is always an implicit
subscriber and cannot be removed. Clearing the stored list removes every other
subscriber, but the owner still receives every result.

A manual run is a real run: it delivers to every subscriber in the snapshot
taken at fire time, and you cannot call that back. To keep non-owner subscribers
from receiving run output, record the current list, clear it with
`heliox automation update <id> --subscriber ""`, and restore it afterwards from
what you recorded.

If even the owner receiving run output is unacceptable, do not fire the
automation. Fall back to the approved output from step 3 as the evidence, and
note the gap in your handover.

Outward steps must be pointed somewhere safe. Disabling stops the schedule, not
the procedure's own side effects. If the procedure sends mail, posts to a public
channel, files a ticket, or moves money, retarget that step at yourself or a
scratch channel for the duration of the loop, and restore the real destination
when you are done.

Never recreate a production automation merely to obtain a clean starting point.
Rebuilding it discards the run history that later cross-run reviews depend on,
and it hands external systems a new webhook URL.

## How many times to run

AI output varies, so one good result can be luck. When that inconsistency would
matter, meaning anything whose output is assembled rather than fixed, run the
representative scenario three times and report the spread rather than the best
one. Use a single run for deterministic, unsafe, or expensive cases, and say why
repeating it would add little confidence or too much risk.

## The loop is serial, and that is not a preference

Each scenario needs its own procedure variant, and every variant is written to
the same procedure document. They collide. So run one scenario at a time, all
the way through capture, before touching the document again.

There is no whole-document write. `document edit` replaces one span at a time
(`--old` must appear exactly once unless you pass `--replace-all`), `document
seed` only fills a document that is still empty, and `document read` renders
with line numbers for inspection, so its output is not something you can write
back. That shapes the whole loop: **every variant is one minimal, uniquely
identifiable span, and you undo it with the inverse replacement.**

Before the first edit, save the approved body to the workspace. Save the text
you authored and passed to `--procedure`, not the output of `document read`.
Then, for each scenario, write down both strings before touching anything:

```bash
# 1. swap in the variant with a targeted replacement
heliox document edit <procedure_doc_id> \
  --old "Read #incidents for messages posted in the last 24 hours" \
  --new "Read #incidents for messages posted between 2026-07-13 and 2026-07-14"

# 2. fire it and capture the execution id from the JSON output. This returns
#    as soon as the server posts the run header; the executor wakes afterwards,
#    in its own thread, and reads the procedure document only once it is awake.
#    The --json output includes execution_id directly — use it instead of
#    guessing from `automation runs`, which is ambiguous when two runs overlap
heliox automation run <id> --json

# 3. WAIT for it to finish before doing anything else. Poll until run show
#    reports a finalized run; an unfinalized one is still working, and both
#    the transcript and the delivered output are incomplete until then
heliox automation run show <execution_id> --transcript --json

# 4. undo the same span, exactly, and only now
heliox document edit <procedure_doc_id> \
  --old "Read #incidents for messages posted between 2026-07-13 and 2026-07-14" \
  --new "Read #incidents for messages posted in the last 24 hours"

# 5. confirm the undo landed before the next scenario
heliox document read <procedure_doc_id>
```

**Step 3 is not optional and it is not a formality.** `heliox automation run`
returns before the executor has read anything. Restoring the span while the run
is still queued or mid-flight means the executor reads the *restored* procedure
instead of your variant, so the scenario silently tests the thing you were not
trying to test, and the grade you record is attached to the wrong text. The
same race truncates the transcript: capture before the run finalizes and you
grade a partial answer as if it were the whole one. Neither failure announces
itself. Wait for the finalized run, then restore.


Keeping each variant to a single span is what makes step 3 possible. A variant
that rewrites half the procedure has no exact inverse, and you will be
reconstructing the original from memory, which is how a two-week window ships
as a one-hour window.

An injected fault must never survive into the approved procedure. The saved
body plus the recorded old/new pair is what protects that, and step 4 is what
proves it.

## Capture

`--json` is not optional. Cards, approvals, and attachments have no plain-text
equivalent, and a run whose real output was a broken card renders as clean text
without it. You would be grading the caption, not the picture.

`run show` returns the fire record and the transcript. It does not return token
counts or durations, and neither does anything else here. Record the metrics
Helio actually gives you; do not report timing or cost figures you had to
estimate.

Keep the evidence outside the procedure, under a workspace beside the
automation:

```
<name>-workspace/
  procedure-approved.md
  iteration-1/
    <scenario>/candidate/{transcript.json,notes.md,grading.json}
    <scenario>/baseline/{transcript.json,grading.json}
```

Label any scenario whose input was injected rather than real in its `notes.md`,
so nobody later mistakes the fault for the procedure.

## Write the expectations while the runs are in flight

A run takes real time. Use it: turn each scenario into statements you could hand
to someone who was not in this conversation, and explain them to the user before
the results land. An expectation the user disagrees with is much cheaper to fix
now than after you have graded against it.

An expectation earns its place by being able to fail. Ask of each one: what
output would this reject?

Bad:
> "Produces a digest of urgent tickets."

Good:
> "Every ticket cited was opened inside the stated window. The oldest timestamp
> in the output is within 24 hours of the run."

The first passes for an empty digest, a stale digest, and a digest covering the
wrong month. The second fails all three.

Reserve expectations for facts that can be observed. Tone, usefulness, and
whether a summary reads well are for the user to judge; do not turn taste into a
score.

## Grade against what was delivered, not what the run says it did

Read the transcript for what the executor did, then go look at what actually
landed: the message in the channel, the document, the file. A transcript is a
self-report.

Bad:
> "The transcript says it posted the summary to #ops-daily. Pass."

Good:
> "The transcript says it posted to #ops-daily. Read the channel: the message is
> there, it cites four tickets, and all four are inside the window. Pass,
> evidence: message `m-8813`."

Record one `grading.json` per run:

```json
{
  "scenario": "no-result",
  "execution_id": "e-4f92",
  "configuration": "candidate",
  "finalized": "success",
  "expectations": [
    {"text": "Reports the quiet period instead of widening the window",
     "passed": true,
     "evidence": "Posted 'No new incidents since yesterday'; transcript shows one read at the stated 24h window and no second read."}
  ]
}
```

`finalized` belongs in there alongside the expectations. A run can produce a
perfect digest and still finalize as failed, or produce nothing and finalize as
success. The finalization is part of the contract the executor is judged on, and
it is the half that subscribers see when things go wrong.

While grading, judge the expectations too. An expectation that passed but would
also have passed for an obviously wrong output is worse than no expectation,
because it manufactures confidence. If you notice one, say so and rewrite it
rather than banking the pass.

## Look past the pass rate

Summarize across scenarios and repeats before concluding anything:

```markdown
| Scenario | Configuration | Passed | Runs | Consistent? | Evidence |
| --- | --- | ---: | ---: | --- | --- |
```

Then ask what the aggregate hides:

- Which expectations passed for both the broken and the working version, and
  therefore discriminate nothing?
- Which scenarios varied between repeated runs?
- Did a fallback in the procedure quietly cover a broken dependency, so the run
  looked green while the source was down?
- Did the delivery destination, the audience, or the side effects drift from
  what the user approved?
- Did the candidate add tool calls or complexity that bought nothing?
- Do the failures cluster on one missing instruction, or one upstream system?

## Show the user

There is no browser here, so the results go into the conversation as one table:
one row per scenario, what came out, what was expected, whether it held, and
what the baseline did.

| Scenario | What it produced | Expected | Held? | Baseline |
| --- | --- | --- | --- | --- |
| representative | 4-item digest, all in window | … | yes | 11 items, ignored the window |
| no-result | "No new incidents since yesterday" | … | yes | widened to 7 days, invented a summary |

When the evidence is substantial, put the cases, execution ids, grades, and
analysis in a Helio document and share that instead of flooding the chat.

Then ask plainly what is wrong with them, at the user's altitude. Empty feedback
means it looked right to them, and a scenario nobody commented on is one you
should not go re-tune on your own instinct.

## Revise and replay

When a scenario fails, fix the smallest *general* defect that covers it, not the
instance. A procedure that handles last Tuesday because you wrote last Tuesday
into it has learned nothing.

Then replay into `iteration-<N+1>/`: the failing scenario, plus one that passed
before. The passing one is the regression check. A fix that repairs the
no-result path and quietly breaks the normal one is a common outcome, and only
replaying both catches it. Re-run the summary and the questions above.

Stop when the user is satisfied, when the feedback comes back empty, or when
further runs stop changing a failed conclusion. That last case is not a failure
to hide: report the blocker, leave the automation disabled, and say what would
have to change.

Keep the stable scenarios and the latest verified execution ids in the workspace
or an evaluation document so a future maintainer can replay them. Leave bulky
transcripts in run history rather than copying them around, and keep all of it
out of the executor's procedure. Every scheduled run should receive only the
instructions needed to do its work.

## Record what the loop taught you

The loop is over when the user has seen the results. Before you leave it, write
what it taught into the automation's experience record:

```bash
heliox automation experience add <automation-id> --body "<what the loop showed>"
```

This is not a formality, and it is not a summary of the grades. A rehearsal is
the one time anybody drives this automation with full attention, and what you
learned doing it is about to leave with your context. Everything a later
executor would otherwise rediscover the hard way goes here.

**What belongs in it.** Four things, and the pass rate is not one of them:

- **Which paths fired and held, and which are still unproven.** A later reader
  needs to know that `source-down` was never exercised, not merely that four
  scenarios passed. An unproven path someone knows about is a known unknown; an
  unnamed one is a surprise at 3 AM.
- **What a scenario made you change, and why.** The procedure that shipped is
  not the procedure you first wrote. The diff is invisible to everyone who comes
  later, and the reason for it is the only thing that stops someone changing it
  back.
- **What the sources actually do, as opposed to what their documentation says.**
  A feed that refreshes more slowly than the automation's cadence, so
  consecutive runs legitimately return identical values. An endpoint that
  answers 200 with an empty body instead of 404. A field present most days and
  absent at weekends. These are exactly the observations that become false
  alarms when nobody wrote them down.
- **What you could not test, and why.** A path that needs a real outage, a
  credential you did not have, a season of the year. Say it plainly rather than
  leaving the coverage looking complete.

**Cite the run ids.** Every claim should rest on a run someone else can go read.
"The source returns stale data" is an opinion; "runs 6a76…, 6a77… and 6a78… all
returned the same timestamp fifteen minutes apart" is evidence, and a later
reader can check whether it still holds.

**One entry, not one per scenario.** The record is a timeline and the whole
rehearsal is one moment on it. Five entries written in the same minute tell a
reader nothing that one entry does not.

**Do not write the grades.** Pass rates belong in what you show the user, not in
the record. A reader six weeks from now cannot act on "4/5 passed"; they can act
on "the empty-result path posts nothing and closes skip, verified in run 6a76…".

**A new automation's entry is its first.** Nothing precedes it, so it is also
the only account of why the procedure looks the way it does. Handing an
automation over with an empty record means everything the rehearsal learned is
gone and the refiner inherits nothing to reason from.
