# What you may do to an automation

Every read of an automation carries the server's decisions for you, under
`permissions`. Those are the answer. The `owner:` and `executors:` lines are
not: working out what you may do from whose name sits where is how an executor
talks itself out of an act it already holds, and then tells the owner it is
blocked.

```bash
heliox automation show <id>       # the `you:` line names every decision you hold
heliox automation list --json     # permissions on every row
```

Five decisions ride. They are not a ladder, so reading one does not tell you
the others:

| Decision | What it opens |
| --- | --- |
| `can_edit` | rename, reschedule, a live manual run |
| `can_delete` | `automation delete` |
| `can_toggle_enabled` | `automation update <id> --enable true` / `false` |
| `can_rehearse` | `automation run <id> --rehearsal --fire-key <k>` |
| `can_manage_subscribers` | `automation subscriber add` / `remove` |

`can_edit` is the automation's manage relation, and it is held by people: its
owner, an org admin, someone the owner granted. An AI does not hold it, not
even on an automation it created a minute ago. So it is the single worst
field to generalize from: it is false in the ordinary case, and in that same
ordinary case `can_toggle_enabled` and `can_rehearse` are true.

Changing who executes it has no decision of its own, and `can_edit` is not
it: the server takes that write only from the automation's owner, in person,
so an org admin or a granted editor is refused there too.

## What being its executor carries

All of this, with `can_edit` false throughout:

- **Write the procedure.** `heliox document edit <document_id>`. The binding
  grants you editor on the procedure document itself, because you are the one
  who has to run it. It follows a reassignment: hand the automation to another
  executor and the grant goes with it.
- **Arm and disarm it.** `heliox automation update <id> --enable true`, or
  `false`. A PATCH carrying only `enabled` is yours. One that also carries a
  name, a cron, or an executor list is somebody else's, and it is refused
  whole rather than partly applied — so change nothing else in the same call.
- **Rehearse it.** `heliox automation run <id> --rehearsal --fire-key <k>`.
  The same command without `--rehearsal` is a live run and belongs to an
  editor.
- **Write its wiki and its scripts.**
  `heliox automation file write <id> wiki/<topic>.md --body "<content>"`, the
  same for `scripts/<name>`, and `heliox automation file delete <id> <path>`
  for a page that turned out wrong.
- **Append both ledgers.** `heliox automation experience add <id>` is yours
  alone: the observations are your testimony, so nobody else may sign them.
  `heliox automation feedback add <id>` records what the owner asked for, and
  you may record it because you are the other end of the conversation they
  said it in; the entry is theirs and is stamped as recorded by you.
- **Read all of it.** The files, the procedure, the run history, the
  transcripts.

## What is somebody else's

Each of these has a person attached, and naming that person is the useful half
of saying you cannot do it:

| Not yours | Whose it is |
| --- | --- |
| When it fires: `--cron`, `--timezone`, a one-shot's start time | `can_edit` — an editor's |
| Its name | `can_edit` — an editor's |
| A live `automation run` with no `--rehearsal` | `can_edit` — an editor's |
| Who executes it | the owner's, in person; an editor is refused here too |
| `suspend` and `resume` | the owner's, or an org admin's |
| Deleting it | `can_delete` — the owner's, in person; an org admin only for one nobody owns, or one whose owner left the org |
| Adding or removing subscribers | `can_manage_subscribers` — the owner's, in person: the server wants a human present for a change to who receives the output, and no authorization makes you one |

## A decision can be true and the write still fail

The decisions say who may work a control, not that it would land right now. A
suspended automation refuses arming, and refuses every fire, until someone with
the matching restore right resumes it. `heliox automation show <id>` prints
`suspended: <reason>` and `--json` carries `suspend_reason`; read that before
concluding a decision was wrong.

## Before you tell anyone you cannot

Say it from a decision you read or an error the server actually returned. "It
belongs to someone else and I am only the executor" is not a reason — that
sentence describes the ordinary case, the one where you hold everything in the
first list. An automation you were handed to run is one you can also fix, prove,
and turn on.
