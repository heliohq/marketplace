# Executing one run

Read this when you have been woken to run an automation, rather than to
change one.

## Work inside the run thread

The run thread is the permanent record of this execution. Do your work there,
not in a side channel. When the output is long, write it into a document and
post the document reference back into the thread so that it stays discoverable
without making the thread unreadable.

## Follow the procedure

The bound procedure document is the authority for what this run does. Read it
before acting. If you cannot read it (the document is missing, empty, or
access is denied), send a DM to the owner explaining what happened and stop.
Do not improvise a run from memory or from the automation's name.

## Record what this run taught you

Before the terminal verb, write what THIS run showed into the automation's
experience record:

```bash
heliox automation experience add <automation-id> --body "<what this run showed>"
```

**Write when this run showed you something**: an error, a source that moved or
changed shape, a result that no longer matches what the owner asked for, an
interface that changed under you, a step in the procedure that no longer
applies. Nothing of the kind: close and write nothing. You are the only party
present while the automation runs, so what you noticed does disappear when this
turn ends. But an entry that says only that the run was fine buys nothing a
reader cannot already get from the run history, and on a three-minute automation
it buries the entries that matter under four hundred that do not.

**The first run of an automation is the exception: always write.** The procedure
has just been written, the failure paths have just been checked, and the record
is empty. That run carries more than any later one, and there is nothing yet for
a reader to compare it against.

**Write only this run.** The record is a timeline: your entry keeps its own
timestamp and your earlier ones stay exactly as you wrote them, so a reader can
see when each thing was learned. Do not restate what still holds (it is
already there) and do not fold several runs into one entry. Cite the run ids
your observations rest on.

**Put it in the right file.** The routing is in
[`where-things-go.md`](where-things-go.md): an observation about this
automation goes in its own files; a pattern across the automations you run goes
in your private wiki. The former survives a handoff, the latter does not.

**When entries have become one lesson, say it once and name them.** Five runs
that each hit the same flaky source are one fact, not five. Consolidate with:

```bash
heliox automation experience add <automation-id> --body "<the one lesson>" \
  --replaces <entry-id>,<entry-id>
```

Comma-separated, no spaces. Separating the ids with spaces makes the second
one a positional argument and the command fails on argument count before it
sends anything.

The named entries stop reading as current but stay in the record under their
own heading, so a later reader can still check your summary against what was
actually seen. Consolidate only your own entries: another executor's account
is theirs, and retiring it is not yours to do.

**Recording is not refining.** This step observes; it does not edit the
procedure. One run cannot distinguish a one-off blip from real decay, and the
procedure is what every future run obeys. When a run reveals something that
must change, record the observation here and take the change through the
refiner's own entry points, where the evidence spans more than one run.

**Escalate what the owner has to decide.** A failure that will repeat, a source
that has gone away, a result that no longer matches what the owner asked for:
mention the owner directly rather than only writing it down. The ledger is read
when someone goes looking; a mention arrives. Judge it by whether the next run
is likely to fail or to produce something the owner would not want sent, not by
whether this run happened to survive.

**Record what the owner asks you for.** When the owner states a requirement in
conversation (this is too long, stop paging me at night, I want the number not
the chart), write it to `feedback.md` in the same turn:

```bash
heliox automation feedback add <automation-id> --body "<what they asked for>"
```

The entry is theirs, not yours: the author is the owner, and you are stored as
its recorder and shown in its signature, so a reader can tell a relayed
requirement from one the owner typed. Transcribe what they said. Do not decide
on their behalf that they did not mean it, and do not wait for them to go find
the ledger themselves: they told you, and you are the one holding the command.

Two limits. A requirement from someone who is not the owner is not owner
feedback: relay it to the owner rather than recording it in their name. And
your own conclusions are not feedback either, however sound: those go to
`experience.md`, which is where a reader expects to find your judgment.

## Then ask: does this run earn a review?

Recording is not refining. That has not changed. One run cannot tell a blip
from decay, and the procedure is what every future run obeys.

What has changed is who decides. There is no timer that wakes someone up after
N runs; you are the party present, you have just written down what happened,
and you can read everything this automation has accumulated. So before the
terminal verb, answer one question: is a review due now?

Some conditions skip the wait entirely: things visible in the run you just
closed that mean the next fire will hit the same problem. Otherwise, the pace
depends on how often the automation runs: a fast one accumulates evidence fast
and earns a look sooner, a slow one earns a look every time. Both lists,
the conditions and the cadence bands, live in Entry 3 of the refiner skill,
with the reasoning behind each.

Either way, **close this run first.** The terminal verb below is not optional
and does not wait for a review: a run that commits without one surfaces later as
unclosed or died and alerts the owner, which is a poor reward for a run that
went fine. The review reads across runs: the one you just closed is simply the
most recent of them, and closing it loses nothing.

Then, when the answer is yes, go through `heliox:automation-refiner`. When it is
no, you are already done.

## Close with exactly one terminal verb

Every run ends with one of these three commands. Omitting the close leaves the
run permanently open, so pick one before you finish.

```bash
heliox automation run success <execution_id>
heliox automation run failed <execution_id> --reason "<what broke>"
heliox automation run skip <execution_id> --reason "<checked what; why quiet>"
```

**success**: the result has been posted in the run thread, and every
subscriber has already been given the summary. Both conditions are required;
posting in the thread alone is not delivery.

Delivering does not have to mean interrupting. Pick by what the reader has to
do with it:

```bash
heliox feed note --to @handle --text "<digest>"   # they need to know; nothing to act on
heliox message send @handle "<digest>" --seen <n> # it must interrupt them
```

A note lands on their Home and clears itself after a day. Either one counts as
delivering to that subscriber: the question is whether the person heard, not
which door carried it.

**failed**: something went wrong that prevented a valid result. You have
sent a DM to the owner describing what broke. Mentioning the owner in the
thread is not sufficient: the DM is what they will see.

**skip**: you checked and there was nothing worth reporting this period. Leave
a line in the thread explaining what you checked and why the period was quiet.
Do not push a summary to subscribers: not as a DM, not as a note; a quiet
period is not a delivery.

The judgment after every run is one question: is this result worth sending to
subscribers? If it is, close with success. If there is nothing to send, close
with skip. You are deciding whether the content is worth delivering, not
whether each subscriber individually wants it.

`--reason` is required on failed and skip. If you omit it, the run stays
unclosed and the automation has no record of what happened.

A run that failed is not the same as a run that found nothing. If the source
errored out, that is failed, not skip: every terminal state the monitored
system can reach needs its own honest close.

If this run exposed a problem in the procedure itself (a step that is wrong,
a source that has moved, a format that no longer works), that is work for
`heliox:automation-refiner`, not something to fix mid-run.
