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
before acting. If you cannot read it — the document is missing, empty, or
access is denied — send a DM to the owner explaining what happened and stop.
Do not improvise a run from memory or from the automation's name.

## Record what this run taught you

Before the terminal verb, write what THIS run showed into the automation's
experience record:

```bash
heliox automation experience add <automation-id> --body "<what this run showed>"
```

Do this on **every** run, including the uneventful ones. You are the only party
present while the automation runs; what you noticed disappears when this turn
ends, and the record is the only thing a later reader — often a later you —
can consult. A cross-run review cannot find a pattern in runs nobody recorded.

**Write only this run.** The record is a timeline: your entry keeps its own
timestamp and your earlier ones stay exactly as you wrote them, so a reader can
see when each thing was learned. Do not restate what still holds — it is
already there — and do not fold several runs into one entry. Cite the run ids
your observations rest on. "Ran clean; nothing new" is a legitimate body and
worth writing: it tells the next reviewer the quiet runs were looked at, not
skipped.

**When entries have become one lesson, say it once and name them.** Five runs
that each hit the same flaky source are one fact, not five. Consolidate with:

```bash
heliox automation experience add <automation-id> --body "<the one lesson>" \
  --replaces <entry-id> <entry-id> ...
```

The named entries stop reading as current but stay in the record under their
own heading, so a later reader can still check your summary against what was
actually seen. Consolidate only your own entries — another executor's account
is theirs, and retiring it is not yours to do.

**Recording is not refining.** This step observes; it does not edit the
procedure. One run cannot distinguish a one-off blip from real decay, and the
procedure is what every future run obeys. When a run reveals something that
must change, record the observation here and take the change through the
refiner's own entry points, where the evidence spans more than one run.

**Escalate what the owner has to decide.** A failure that will repeat, a source
that has gone away, a result that no longer matches what the owner asked for —
mention the owner directly rather than only writing it down. The ledger is read
when someone goes looking; a mention arrives. Judge it by whether the next run
is likely to fail or to produce something the owner would not want sent, not by
whether this run happened to survive.

**Record what the owner asks you for.** When the owner states a requirement in
conversation — this is too long, stop paging me at night, I want the number not
the chart — write it to `feedback.md` in the same turn:

```bash
heliox automation feedback add <automation-id> --body "<what they asked for>"
```

The entry is theirs, not yours: the author is the owner, and you are stored as
its recorder and shown in its signature, so a reader can tell a relayed
requirement from one the owner typed. Transcribe what they said. Do not decide
on their behalf that they did not mean it, and do not wait for them to go find
the ledger themselves — they told you, and you are the one holding the command.

Two limits. A requirement from someone who is not the owner is not owner
feedback: relay it to the owner rather than recording it in their name. And
your own conclusions are not feedback either, however sound — those go to
`experience.md`, which is where a reader expects to find your judgment.

## Close with exactly one terminal verb

Every run ends with one of these three commands. Omitting the close leaves the
run permanently open, so pick one before you finish.

```bash
heliox automation run success <execution_id>
heliox automation run failed <execution_id> --reason "<what broke>"
heliox automation run skip <execution_id> --reason "<checked what; why quiet>"
```

**success** — the result has been posted in the run thread, and every
subscriber has already been given the summary. Both conditions are required;
posting in the thread alone is not delivery.

Delivering does not have to mean interrupting. Pick by what the reader has to
do with it:

```bash
heliox feed note --to @handle --text "<digest>"   # they need to know; nothing to act on
heliox message send @handle "<digest>" --seen <n> # it must interrupt them
```

A note lands on their Home and clears itself after a day. Either one counts as
delivering to that subscriber — the question is whether the person heard, not
which door carried it.

**failed** — something went wrong that prevented a valid result. You have
sent a DM to the owner describing what broke. Mentioning the owner in the
thread is not sufficient — the DM is what they will see.

**skip** — you checked and there was nothing worth reporting this period. Leave
a line in the thread explaining what you checked and why the period was quiet.
Do not push a summary to subscribers — not as a DM, not as a note; a quiet
period is not a delivery.

The judgment after every run is one question: is this result worth sending to
subscribers? If it is, close with success. If there is nothing to send, close
with skip. You are deciding whether the content is worth delivering, not
whether each subscriber individually wants it.

`--reason` is required on failed and skip. If you omit it, the run stays
unclosed and the automation has no record of what happened.

A run that failed is not the same as a run that found nothing. If the source
errored out, that is failed, not skip — every terminal state the monitored
system can reach needs its own honest close.

If this run exposed a problem in the procedure itself — a step that is wrong,
a source that has moved, a format that no longer works — that is work for
`heliox:automation-refiner`, not something to fix mid-run.
