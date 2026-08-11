# Where each thing goes

Seven places, and one question sorts most of them: *is this true only for this
automation, or for this person?*

| What you have | Where it goes |
| --- | --- |
| A rule every run follows | `procedure.md` |
| What this run hit | `experience.md`, signed, citing its run ids |
| What the owner counts as good | `feedback.md`, in their words |
| A fact about this automation's world | `wiki/<topic>.md` |
| Work every run re-derives | `scripts/<name>` |
| A pattern across the automations you run, or how this person likes to work | your own private wiki |
| A team or project fact other people should see | workspace memory, or `heliox memory` |

The first five ride with the automation: hand it to another executor and they
arrive intact, signed and readable. The sixth does not — your private wiki is
yours, and the executor who takes over starts with an empty one. That is the
whole reason an automation-specific observation belongs in the automation's own
files, and it is the mistake worth watching for in yourself.

The reverse is a mistake too. "They want numbers, not charts, in everything"
is about the person, and filing it under one automation's feedback hides it
from the other four.

## Why the fast band has two limits

"Whichever comes first" is for the quiet ones. An hourly automation that sleeps
through the night takes days to reach twenty runs, so the day is the backstop
that keeps it from going unread simply because it went unused.

## Reading them during a review

The two prefixes are part of the evidence, not background colour.

A **wiki page you did not open cannot be found wrong.** The refiner's ranking
puts the wiki last precisely because a fact a run just disproved is only out of
date — but that is a correction someone has to make, and nobody makes it from a
page they skipped. The same read is what surfaces a page that has quietly grown
an instruction, which is a second authority rather than a stale fact.

A **script matters when the procedure names one.** Read it before concluding a
step is wrong: the defect may sit in the script rather than in the step that
calls it, and editing the step then papers over a bug that stays.

## Promoting into each of them

**A procedure promotion goes through `heliox document edit`**, like any other
procedure change (the refiner's step 5). `automation file write` refuses the
reserved paths, so aiming it at `procedure.md` returns an error rather than
promoting anything.

**A wiki page or a script is written with**
`heliox automation file write <automation-id> <path> --body "<content>"`. An
existing path is replaced — that is how a page is maintained, and why there is
no separate create verb.

**A promoted script is a change to prove, not a trace to leave.** It alters what
every future run executes, so it belongs back in the make-and-prove steps: write
it, point the procedure at it, and rehearse that path before finishing.
Promoting a fact into the wiki needs no rehearsal — it changes what the executor
knows, not what it does.
