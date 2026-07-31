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
