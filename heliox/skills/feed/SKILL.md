---
name: feed
description: "Use `heliox feed ...` to put something on a person's Home without interrupting them: `note` for what they only need to know (clears itself after 24h), `suggest` for something they should decide on (accepting it is what turns it into work). Trigger when you have a result, a digest, or an idea for someone and a DM would be louder than it is worth — especially when closing an automation run."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox feed --help"
---

# Heliox Feed

## Model

Feed is the quiet door onto a person's Home. Everything you raise there is a
**proposal**: nothing you run ever puts a task on someone's list — only their
own accept does.

Two verbs, differing in one thing: whether clearing it produces a piece of work.

| Verb | You are saying | How it leaves them |
| --- | --- | --- |
| `note` | you need to know this | reaped automatically after 24 hours; asks for nothing |
| `suggest` | should we do this? | they accept (it becomes a task) or dismiss it |

```bash
heliox feed note    --to @alice --text "<what happened>" --source-label "<where it came from>"
heliox feed suggest --to @alice --to @bob --text "<the thing to be done>"
```

`--to` takes a `@handle` and repeats for several people; each recipient gets
their **own** item, so one push to three people is three separate readers, not a
shared row. Bare 24-hex user ids are rejected — address people the way the rest
of the surface does. `--text` is required. `--source-label` is the only
provenance the row shows (a feed row carries no link), so write it as the place
a person would go looking: `--source-label "nightly deploy check"`.

## The ladder

Pick by what the reader has to **do** with it, quietest first:

| | When |
| --- | --- |
| say nothing (`heliox automation run skip`) | routine, everything normal |
| `heliox feed note` | worth knowing, nothing to act on |
| `heliox feed suggest` | you want a decision |
| `heliox message send` | it really must interrupt them right now |

A subscriber digest nobody has to act on is a **note**, not a DM. A run that
broke still DMs the owner — someone whose automation failed should be
interrupted.

Write `--text` as the thing itself in the reader's language. On accept it
becomes the task's **title**, so `"rotate the staging cert"` beats
`"cert rotation status report"`. It is capped at 2000 characters and refused
above that, not truncated — a feed row is one line someone reads, so keep the
detail in the run's own thread and make this the headline.

## Inside an automation run

Identity comes from the run, never from you: there is no `--source-key` flag and
no `--proposed-surface-id` flag. Inside a run, both are read from the turn's own
run context, so:

- **Pushing again from the same run updates the same item** instead of stacking a
  second copy on someone's Home. A retry after a failure is safe.
- **One run leaves one item per person.** A second push to the same person in the
  same run *replaces* the first — it restates the row, it does not add one. If
  two things both matter, either say them in one item, or send the urgent one as
  a DM and leave the record in the run's own thread.
- **Accepting binds to this run's thread**, so the person lands where the context
  already is instead of in a fresh empty channel.

Outside a run there is no identity: two notes to one person are two items, and a
retry duplicates.

Both verbs count as delivering to a **subscriber** for the run-delivery check —
the question is whether the person heard, not which door carried it. They do
**not** close the owner leg of a `failed` run: that leg exists to interrupt, and
a note is the rung that does not. A `skip` run pushes nothing at all, not even
a note.

## Traps

- **`--text` split by the shell is refused, not truncated.** Neither verb takes a
  positional, so an unquoted `--text` that the shell breaks into extra tokens is
  rejected. Quote it; if the body carries `$` or backticks, write the whole
  invocation as a JSON array and run `heliox --args-file <path>`.
- **Recipients must be people.** An AI teammate has no Home; a push naming one is
  refused outright rather than landing somewhere nobody can see.
- **All-or-nothing on the names, not on the writes.** The recipient list is
  checked in full before the first item lands, but the fan-out itself is not
  atomic. If a push fails partway, retry it — inside a run the same item
  converges instead of duplicating.
- **You cannot un-push.** There is no delete verb: a note ages out on its own,
  and a suggestion waits for the person's verdict. Reraise a corrected version
  from the same run rather than sending a second, contradicting one.
- **A verdict already given is not reopened.** If the person accepted or
  dismissed this run's item, a re-push updates that row but does **not** put it
  back on their Home — the command says so when it happens. Take it as the
  answer: if the correction really must reach them, `heliox message send`.
