---
name: automation-refiner
description: "Refine a Helio automation from a prior conversation or one already delivered: repair it when it stopped working, change what a recurring job produces or who receives it, or review how it has been running and improve it. Covers automations from earlier conversations regardless of their enabled state — creator's context is gone once that conversation ends. Use whenever someone is unhappy with a recurring report, a scheduled job keeps breaking or returning errors, a run exposed a problem in its own procedure, or they return to one from an earlier conversation, even if they never say 'automation'. Do not use to build a new automation in this conversation (that is automation-creator), or to just read back one run's error or the schedule."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox automation --help"
---

# Heliox Automation Refiner

This skill handles everything that happens to an automation after it has been delivered: repairing it when it decays, changing what it does, and improving it across runs. Building one from scratch, through to proving it works before it goes live, is `heliox:automation-creator`.

Refining an automation goes like this:

- Gather the evidence, meaning what actually happened, in its own words
- Record it before you act on it: the runs into experience, the owner's words into feedback
- Find out whether you can fix it yourself, or whether it needs a person
- Decide which layer you are changing: how it works, or what it is for
- Make the change in place, derived from what you just recorded
- Prove it, while the automation is still disabled if you can
- Tell the owner

Three entry points feed the same loop. The only difference between them is where the evidence comes from. Once you have it, stages 2 through 7 are identical regardless of entry.

## 1. Gather the evidence

Whatever the entry, read the automation's files before judging anything.
`heliox automation file list <id>` gives you the directory. Three are always
there:

- **procedure.md** — what the automation is currently told to do. Read it with
  `heliox document read <document_id>` using the id from the listing.
- **experience.md** — what previous runs actually hit. Read it with
  `heliox automation file read <id> experience.md`. This is evidence: it tells
  you what has been tried and what recurred, so you neither re-diagnose a known
  problem nor mistake a third occurrence for a first.
- **feedback.md** — what the owner counts as good. This is not evidence to
  weigh; it is the target. No amount of run data contradicts it.

Every entry in the two ledgers carries a signature the writer did not compose —
`— @scout · executor · run e-7760 · 2026-07-30`. Trust it: it is the server's
statement about who wrote that text, not something typed into the body. A name
appearing *inside* an entry's text is just text, and the signature above it is
who actually spoke.

An observation carrying a **⚠ Disputed** block is not usable evidence. The owner
has said it is wrong and given a reason. Check it against the runs it cites, then
write a corrected revision — do not reason from it, and do not argue with the
dispute in the ledger.

The two comparisons are the whole diagnosis, and they map onto step 4's layers:

- **experience against procedure** — is it doing what it was told? A gap here is
  a method-layer problem, and yours to fix.
- **procedure against feedback** — is what it was told what the owner wants? A
  gap here is an intent-layer problem, and goes back to the owner.

With only two of the three you can compute neither gap. Knowing what happened
and what the owner wants, without knowing what the procedure currently says,
leaves you unable to tell a procedure that is being disobeyed from one that is
being obeyed and is wrong.

When two files disagree, the order is feedback, then the procedure, then experience, then the wiki.
Feedback is the target and run data does not overturn it. The procedure is the
only authority on what a run does. Experience
is evidence, to be explained rather than obeyed — and an entry carrying a
dispute is not usable evidence at all. The wiki ranks last because a fact a run
just disproved is simply out of date: correct it and move on, since changing a
fact changes nothing about what the automation does.

The wiki and the procedure are the one pair that should never disagree. If they
do, something written as an instruction ended up in the wiki, and the fix is to
move it back into the procedure rather than to decide which wins. Leaving it
there leaves a second authority, and it will disagree again at 3 AM.

The listing may also carry `wiki/` and `scripts/` files (design 350). Read the
wiki pages bearing on this review — `heliox automation file read <id>
wiki/<topic>.md` — and any script the procedure names: a page you never opened
cannot be found stale, and the ranking below asks you to place the wiki against
the other files. [`references/where-things-go.md`](references/where-things-go.md)
says which file holds what.

An automation that has never been reviewed has empty ledgers. That is normal,
not a fault: read the procedure and start the experience ledger with what this
round observed.

### Entry 1: the user asked for a change

The first thing to establish is whether they are unhappy about this one result, or about every run from now on. A complaint about one result may not require any change to the procedure, because the run may have been correct and the output simply surprising. A complaint about every run is a procedure change.

The run channel is visible to the whole org, so the person speaking up may not be the owner. Changes ultimately serve the owner's intent, so when the request comes from someone else, confirm with the owner before editing.

### Entry 2: you are testing, or you saw something wrong

A run executes in its own thread and its outcome will not appear in front of you on its own. You need to go and get it:

```bash
heliox automation runs <id>
heliox automation run show <execution_id> --transcript --json
```

The `--json` flag matters: cards, approvals, and attachments have no plain-text equivalent, and without it you may give a broken run a passing grade because you only saw the text portion of its output.

Two risk levels shape how freely you can iterate.

Still disabled means the automation has never been enabled, or you disabled it for testing. Nothing fires on its own, so you can iterate at your own pace. A manual run is still a real run, though: it delivers to every subscriber in the snapshot. Step 6 covers how to rehearse without that.

Already enabled means the next scheduled run will deliver real output to real subscribers. Changes need to be conservative, and you should tell the owner what you changed and why before the next run fires.

### Entry 3: looking back across runs

A single run cannot distinguish a one-off glitch from a pattern. A source that fails today and recovers tomorrow looks the same in one run as a source that fails every week, but the first does not justify a procedure change while the second demands one. Separating the occasional from the systemic requires a cross-run perspective.

When the user asks for a review ("look at how this has been running lately"), gather the evidence through the `runs` and `run show` commands above: list recent executions, inspect representative transcripts, and look for repeated patterns versus one-off glitches.

### How often to look

Nobody schedules this review, so the pace is yours to set, and the two ways to
get it wrong are opposite. Editing a procedure every run, when the automation
fires every three minutes, means a single flaky afternoon becomes a permanent
workaround. Never looking at a weekly digest means a year of runs nobody read.

Scale the gap to the cadence. The cost of a review is fixed — three files and
some recent runs — while what it buys grows with the evidence available, and a
fast automation accumulates evidence fast:

| How often it runs | How long to let it run before a review |
| --- | --- |
| Every few minutes, or hourly | a day, or 20 runs, whichever comes first |
| Daily | about a week |
| Weekly or slower | every run is worth a look |

Treat these as the right order of magnitude rather than a count to keep. The
difference between 20 runs and 25 does not matter; the difference between 20
and 2 is the whole point.

### What does not wait

The table above is for when nothing has gone wrong. Any of these, and the
review happens now:

- **Wrong output reached real subscribers.** Whatever produced it will produce
  it again on the next fire.
- **An outward or irreversible effect happened, or nearly did** — mail sent, a
  payment moved, something published. This is the blast radius the automation
  was created with, and it is why that question gets asked at creation.
- **The same failure twice in a row.** Once is weather; twice is the procedure.
- **The owner has said something.** A new entry in feedback means the target
  moved, and running to an old target is not worth waiting out a budget for.
- **A run closed failed for a reason that will repeat.** When you cannot tell
  whether it will, look — one extra review costs less than a month of a decay
  nobody caught.

These are things you can see in the run in front of you, rather than a severity
score. A score needs a scale, a scale needs a judgment call, and there is
nobody awake at 3 AM to check that judgment. The third is the one exception —
it needs the previous run — but that is exactly what experience.md is for: the
earlier entry is already there with its own timestamp.

Being due is a reason to look, not a reason to change. Everything below about
what justifies an edit applies unchanged: a review that finds nothing is a
finished review.

**A review that changed nothing does not go to the owner.** Write what you
looked at into experience, so the next one does not re-read the same history,
and stop there. Step 7's "tell the owner" is about changes: on a three-minute
automation, a message per uneventful review carries no decision and teaches the
owner to stop reading them. Someone who asked for the review still gets an
answer — replying to a person who asked is not an owner notification.

## 2. Record it before you act on it

The two ledgers get written **before** the procedure is touched, not after. A
procedure edit is supposed to be derived from what the runs showed and what the
owner asked for; writing those down first is what makes that true rather than
merely claimed. Do it in the other order and the edit rests on your memory of
this conversation, which ends with it — leaving a changed procedure whose reason
exists nowhere.

**Acting starts before the edit does.** Reading the runs and settling on what
should change is already acting on them. Once you hold a candidate rule, the
owner's words arrive as support for it rather than as the thing it has to meet,
and you will not notice the difference — the reading feels like observation
right up until it decides what you record. Write both ledgers before you
interpret, not merely before you edit.

**The owner's words go into feedback.** When the owner has stated something
durable — what the output should contain, when it should stay quiet, what counts
as good — record it as their entry. Put the requirement in the owner's own
terms, and include enough of when and where they said it for a reader to find
the original. The signature will show you as the recorder, so do not write
"yanghe said" into the body — an attribution inside the text on top of the
server-stamped signature above it is the ambiguity the signature exists to
remove. Transcribe faithfully; do not decide on their behalf that they did not
really mean it. A requirement recorded wrongly is one they can see and fix; one
you silently withheld is neither. If you cannot tell whether it was about this
run or about every run, ask — that distinction changes what gets written, and
asking costs one exchange.

**Only if you are this automation's owner or its current executor.** The server
grants this write to those two and nobody else, for the same reason it restricts
experience: an entry nobody can attribute to a party to the automation is worth
nothing. When you are refining someone else's automation — a common review path
— `heliox automation feedback add` will 403, and it will do so at the START of
this step, before any procedure work. Do not find that out by running it. Put
the owner's wording in your reply instead, addressed to the owner and the
current executor, and let one of them record it.

**What the runs showed goes into experience.** Cite the run ids it rests on.
This is the same write the end of every run performs; here it carries the
cross-run reading a single run could not produce.

Only then edit the procedure, and only for what those two now say.

## 3. Find out whether you can fix it yourself

Your default is to fix it. An automation decays naturally as the services, channels, and people it depends on change around it. The owner created it so they would not have to watch those things, so repairing that decay is your job and escalating is the fallback, not the first move.

The question is simple: can the problem be solved by editing the procedure?

| What actually went wrong | Can you fix it? | What to do |
| --- | --- | --- |
| The service it reads changed its API, its URL, or its response shape | Yes | Update the steps to match the new interface |
| A channel, document, or person it points at was renamed or moved | Yes | Update the reference to the current name or location |
| A step was too vague and the run went sideways | Yes | Make the step explicit enough that the next run cannot misread it |
| Expired credentials, or access that was revoked | No | Tell the owner, name the specific access you need |
| The source is gone and picking a replacement is a decision only a person can make | No | Tell the owner, bring your recommendation for what to use instead |
| The source failed just this once | Do not change it | Report this run as failed and move on |
| A past run closed `success` while what it delivered was wrong | Not the verb — a closed run stays closed | Say the close was wrong. A run that delivered a mistake is a failed run whatever its push returned, and left alone the history reads cleaner than it was — including to the cadence budget, which counts those runs |

When you escalate, say why you cannot fix it yourself, whether it is a missing permission, a revoked credential, or a judgment call that needs a person. "I cannot fix this" without a reason gives the owner nothing to act on.

The last row deserves emphasis. When a source fails once and recovers, do not touch the procedure. Adding a workaround for a one-off failure means that workaround stays in the procedure permanently, and from that point forward it hides the real health of the automation. You can no longer tell whether the source is stable, because the procedure silently papers over its failures. A single bad run is a failed run, not a reason to redesign. Repeated failures across runs are decay, and decay belongs in the rows above.

## 4. Decide which layer you are changing

The method layer is how the automation reads its sources, where it reads from, how it formats the output, how it decides a period was quiet, and how it retries on transient errors. These are the means of getting the owner's intended result. You can change them yourself.

The intent layer is what the automation produces, who receives it, what counts as good enough, and what counts as something worth raising to subscribers. These are the things the owner agreed to when the automation was created. Bring your recommendation back to the owner rather than changing them on your own.

When a change needs you to settle what the owner meant, that is intent whichever layer the mechanism belongs to. "Dial it back" and "only the ones that matter" name a result without giving the rule that produces it, and inventing the missing rule decides what counts as worth raising. Ask for it. The same holds when an edit changes what the output is evidence of — reading the system of record instead of a tracker someone updates by hand is a read-path change on paper, and a change of authority in practice.

Every self-edit requires evidence. Change something because of something you observed, like a step that failed, a source that returned an unexpected shape, or a format that lost information. Do not change it because you think it could be nicer. No one is watching in real time to catch a well-intentioned tweak that silently changes the output, and the next run delivers directly to subscribers.

Bad:
> "The summary could be more concise. I will tighten the formatting instructions."

Good:
> "Run e-4f92 produced a 1,200-word summary for a period with two minor updates. The procedure says 'summarize,' but does not cap length relative to the input volume. I will add a guideline: keep the summary under 200 words when the period has fewer than five items."

Bad:
> "I will switch the source from the REST API to the GraphQL endpoint because it returns richer data."

Good:
> "Run e-7a01 failed because the REST endpoint now returns 404 on /v2/reports. The service moved this data to /v3/reports with a different response shape. I will update the procedure to use the new endpoint and adjust the field mapping."

## 5. Make the change

Edit the bound procedure document in place with `heliox document edit <document_id> --old "<exact span>" --new "<replacement>"`. There is no whole-document write: `--old` must match a unique contiguous span of the rendered text, and `document read` renders with line numbers, so its output is for inspection rather than something you can write back. Preserve the automation and trigger identities, because rebuilding them from scratch discards the run history that future cross-run reviews depend on. Recreate only when the change genuinely requires a new automation, meaning a different job, a different cadence, or a different owner.

Not everything lives in that document, and editing the wrong place fails silently: the edit succeeds and the behaviour does not change.

Who receives the results is stored on the automation, not in the procedure. Writing "send this to Sarah too" into the steps changes nothing, because every fire snapshots the stored audience. Use `heliox automation subscriber add <id> @sarah` or `heliox automation subscriber remove <id> @sarah`, or replace the whole set with `heliox automation update <id> --subscriber <handles>`. Check the result with `heliox automation subscriber list <id>`, which shows the effective audience including the owner, who is always implicit. Removals matter most here: someone the owner wanted taken off the list keeps receiving the output until this command runs.

What an event trigger's handler code does lives in the deployed handler, not in the procedure. The deployed artifact is the source of truth: a refinement often runs in a later runtime where the original source is not on disk, and rebuilding from the template silently discards whatever the handler accumulated, signature verification most dangerously. Fetch the current artifact first with `heliox automation trigger show <trigger-id> --code`, unpack the downloaded zip, make your edits to `handler.mjs`, repackage it, then redeploy with `heliox automation trigger update <trigger-id> --code <handler.zip>`. The `--code` flag is what redeploys the handler in place; without it the command is metadata-only and the broken handler keeps running. The in-place redeploy preserves the trigger's stable URL and token.

The schedule itself lives on the underlying trigger, not in the procedure document. The CLI does not currently support changing the cron expression on an existing scheduled automation: `heliox automation update` accepts `--name`, `--executor`, `--subscriber`, and `--enable`, but not `--cron`. If the owner asks to change the cadence, the current path is to create a new automation with the updated schedule, validate it while it is still disabled, disable the old one with `heliox automation update <old-id> --enable false`, then enable the replacement. That order matters: enabling the replacement before disabling the original leaves both schedules live and fires the same job twice, including every external side effect. Disabling beats deleting because the old run history stays readable and the cutover is reversible if the replacement misbehaves. Writing "run at 8:30 instead of 9:00" into the procedure does not change when the trigger fires.

Before each edit, name the experience or feedback entry it comes from — an edit with no entry to cite rests on this conversation alone, and the conversation ends.

Before editing, capture your baseline: the current procedure text and at least one representative recent run. You need both so that after the change you can tell whether things improved, and if something regresses you can trace it back.

## 6. Prove it

How much proof a change needs depends on what changed and what is at stake. Give the user a one-sentence recommendation with a reason, and let them decide:

- A typo fix or a renamed channel reference is low risk, and a single readback of the procedure may be enough.
- A logic change to the procedure (new steps, changed filters, different formatting) benefits from at least one rehearsal run while the automation is still disabled.
- A change prompted by a production failure should reproduce the failure on the current procedure, apply the smallest general fix, then replay both the failing case and a representative successful case to confirm the fix does not regress normal output.

A rehearsal is a real run and closes like one. Judge it on its ending as well as its output: a rehearsal that produced the right text but finalized without the result reaching the thread, or closed green while a subscriber got nothing, has reproduced the defect rather than fixed it.
- A behavioral redesign, meaning a change to what the automation produces or how it evaluates its sources, calls for the full evaluation loop.

When you can rehearse, do it while the automation is disabled: `heliox automation run <id>`, then fetch the transcript through Entry 2's commands to read the result. Disabling stops the schedule from firing on its own, but a manual run is still a real run. A fresh executor wakes up in its own thread and follows the full contract, including delivering the result to every subscriber in the fired-time snapshot. You cannot intervene in that delivery from the outside.

The loop itself is shared with `heliox:automation-creator` — read [`../automation-creator/references/evaluation.md`](../automation-creator/references/evaluation.md). Three things are yours to decide:

Your proving plan needs two scenarios: the failure you are fixing, and one case that was passing before. Test both — a fix that never reproduces the failure is a guess, and one that regresses a passing case is incomplete.

Your inputs are the real conditions that produced the failure. Reproduce the failing case against the *current* procedure before you edit anything.

Your baseline is the current production procedure, retained verbatim before the edit and labelled `baseline`. When replaying would repeat a harmful side effect, the observed production failure *is* the baseline. Do not re-fire the damage to obtain a cleaner one.

## 7. Leave a trace and tell the owner

Write what you learned into the automation's experience ledger:

```bash
heliox automation experience add <automation-id> --body "Derives from <entry-id>. <what this change concluded, not what still holds> (runs <run-id>, <run-id>)"
```

Good:
> "Derives from exp-12. The /v2 endpoint now paginates at 50 — procedure assumed a flat list and dropped page 2. (runs e-7760, e-7814)"

**Only if you are this automation's current executor.** experience.md is the
executor's testimony and the server enforces that: it is where the observations
a reader is asked to trust come from, so an entry signed by anyone else would
mean nothing. If you are refining someone else's automation — a common review
path, and one where the procedure edit may already be done — do not run this and
watch it 403 at the very end. Put what you concluded in your reply to the owner
instead, addressed to the executor, and let them record it. The observation is
theirs to sign.

**A write appends; retiring is a separate, explicit act.**

What this change made **obsolete** is the part that needs saying out loud. An
observation your fix resolved stays live evidence until you name it, and the
next refiner will read it as a problem that is still happening. Retire it in
the same write:

```bash
heliox automation experience add <automation-id> --body "<what you now understand>" \
  --replaces <entry-id>,<entry-id>
```

The named entries stay in the record under their own heading, so the fix and
what it fixed are both readable. Only your own entries — another executor's
account is not yours to retire.

One thing does not go there: a lesson important enough to matter on **every**
run belongs in procedure.md, and putting it there is this step's real work.
Experience is raw material; the procedure is the finished thing. A note in
experience saying "the source is flaky on Wednesdays" with no matching handling
in the procedure reads to the next maintainer as though it were already handled.

Before finishing, ask three questions of every entry you just wrote — skip none:

1. Does every future run need this, and is it an instruction?
   It **belongs in the procedure** — move it there.
2. Does every future run need this, and is it a fact — how a source behaves,
   what a term means, which ids matter? It **belongs in the wiki**,
   at `wiki/<topic>.md`.
3. Does every future run re-derive this same computation?
   It **belongs in a script**, at `scripts/<name>` — extract it and point
   the procedure at it.

Each destination has its own command and proof obligation.
[`references/where-things-go.md`](references/where-things-go.md) has both.

Then retire what you promoted, in the same write:

```bash
heliox automation experience add <automation-id> --body "<where it went>" \
  --replaces <entry-id>,<entry-id>
```

**Feedback belongs in step 2.** The owner's words go into feedback when you
first record evidence, not here at the end. If the owner stated something
during this process that you have not yet recorded, do it now. When someone
other than the owner asks for a change, including in the run channel, take it
to the owner with your recommendation and let them decide.

Tell the owner, especially when the automation is already enabled, because the next run will execute the new procedure. For method-layer changes, a brief message with the what and why is enough. For intent-layer changes, wait for the owner's approval before writing the edit; the owner's sign-off is what makes an intent change legitimate.

## Executing one run

When you have been woken to execute a run rather than to change the automation, follow [`references/executing-a-run.md`](references/executing-a-run.md). Its core is short enough to carry here, because every run you fire while refining closes the same way.

**The result goes in the run's own thread.** That thread is the audit record and is never left empty: a result sent only as a DM leaves the owner opening a finished run and finding nothing.

**Then record what the run showed you** — the run hit something abnormal (an
error, an API that refused, a tool you had to work around), or the result does
not hold up against the procedure and the owner's feedback — before the
terminal verb:

```bash
heliox automation experience add <automation-id> --body "<what THIS run showed>"
```

Nothing of the kind: close and write nothing. An entry saying only that the run
was fine buys nothing a reader cannot get from the run history. The first run is
the exception: always write.

You are the only party present while it runs, and what you noticed dies with the
turn. Write only what this run showed, and cite the run ids it rests on. Do not
restate what you already recorded: this appends.

Recording is not refining. One run cannot tell a blip from decay, so this step
observes and does not edit the procedure. What it does decide is whether a
review is due now — by the conditions and the pace in Entry 3. What the owner
has to decide gets a mention, not just a ledger line.

**Close this run first, whichever the answer is.** The terminal verb does not
wait for a review. When a review is due, enter it after the close.

Exactly one terminal verb ends it:

```bash
heliox automation run success <execution_id>   # the result is in the run's own thread, and every subscriber has been DM'd a digest
heliox automation run failed  <execution_id> --reason "<what broke>"      # the owner has been DM'd what broke; a thread mention does not count
heliox automation run skip    <execution_id> --reason "<checked what; why quiet>"  # a one-line all-clear in the thread, no digests
```

`message cede` does not: it finalizes the turn while leaving no record, so the owner opens a finished run and finds nothing. A quiet period is a `skip` with a reason, not a decline.

## Output language

- Name, description, and procedure follow the user's own instruction language, not a wrapper sentence around it. A mixed-language instruction follows its dominant language.
- If the instruction is too short to tell (a one-line edit), fall back to the language the conversation is in.
- This applies to artifacts only. Conversational replies stay in the conversation's language, so the two can differ.

## Boundaries

A procedure is a maintained document, not a rule engine. It describes what to do in prose that an AI executor reads and follows. If a change turns the procedure into conditional logic or branching control flow, the work should be code, not a procedure edit.

**A procedure holds rules, not the reasoning that produced them.** It is read at
the start of every run by an executor who needs to know what to do — not why the
rule exists, who asked for it, or what evidence supports it. Those have their own
files, and putting them here both bloats the thing that gets read hundreds of
times and blurs which file is authoritative for what. Four shapes to keep out:

- **Provenance.** "Because @yanghe said so in a DM on 2026-08-02" belongs in
  feedback, as their cited entry. The procedure states the rule.
- **Evidence.** Run ids, measurements, "the source refreshes hourly so the
  timestamps are 40 minutes stale" — experience, cited there.
- **Tooling limits.** "The cron cannot be changed in place" is something the
  *refiner* needs and the executor cannot act on. Experience.
- **Anything undecided.** "22:00–07:00 is a default I picked; the owner has not
  confirmed it" hands the executor a value it can neither use with confidence
  nor resolve, and it will still say "not confirmed" long after it was. Ask, then
  write the answer. A procedure has no provisional state.

The test for a line: *could the executor act differently because of it?* If not,
it belongs in one of the other two files. Keep the rule, move the reason —
including when a ledger write is unavailable and the procedure is the only thing
you can write to. Reaching for it as a fallback is right; carrying the citations
and rationale along with the rule is not.

Seven places to write, and one question sorts most of them:
*is this true only for this automation, or for this person?* Five ride with
the automation, one (your private wiki) rides with you, and one (workspace
memory) belongs to the workspace — see [`references/where-things-go.md`](references/where-things-go.md).

One automation is one job. If what the user is asking for is actually a different job, with different sources, different output, or a different audience, that is a new automation, and the path back is `heliox:automation-creator`.

---

Keep these seven steps in your working list so you do not skip the recording or the owner notification:

1. Gather the evidence
2. Record it before you act on it — runs into experience, the owner's words into feedback
3. Find out whether you can fix it yourself
4. Decide which layer you are changing
5. Make the change
6. Prove it
7. Tell the owner

Please add these steps to your todo list before you start so nothing gets skipped.
