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

Feed is the quiet door onto a person's Home — the screen they start their day
on. A row there renders as exactly three stacked lines: your `--text` in
bold, your `--description` under it, your `--source-label` in small type.
Every row can be dismissed; only a suggestion also carries the ✓ that turns
it into work. Everything you raise there is a **proposal**: nothing you run
ever puts a task on someone's list — only their own accept does.

**One row carries one thing.** The reader answers a row with one glance and
one verdict. A row that bundles three findings gives them nothing they can
say yes to — raise three rows instead; they arrive together anyway.

Two verbs, differing in one thing: whether clearing it produces a piece of work.

| Verb | You are saying | How it leaves them |
| --- | --- | --- |
| `note` | you'll want to know this | fades on its own after 24 hours; asks for nothing |
| `suggest` | should we do this? | they accept (it becomes a task) or dismiss it |

`--to` takes a `@handle` and repeats for several people; each recipient gets
their **own copy of every row in the push**, judged separately. Recipients
must be people — an AI teammate has no Home.

## Writing the row

The reader decides on exactly three lines, and each answers a different
question:

| Flag | Answers |
| --- | --- |
| `--text` | what to do (for a note: what happened) |
| `--description` | why it needs them |
| `--source-label` | what it is about |

**`--text`** is a title, not a summary — one line, in the reader's
language. A suggestion's text is an order and starts at the verb: on
accept it becomes the task's title verbatim and the work is handed to
their assistant, so write the order the reader would give if they typed it
themselves — `"Rotate the staging wildcard cert"` beats `"Certificate
status update"`, and both beat `"I found that the staging cert is
expiring"`. A note's text is not an order; it states what happened. If you
cannot phrase it as one order one person would give, split it: two orders
are two suggestions; no order at all is a note.
Everything past the order itself — the date, the amount, the evidence —
belongs in `--description`, which is why text is refused above 120
characters while description takes 2000.

**`--description`** is the case for saying yes, and it must add a fact
`--text` does not already carry — a date, an amount, a count, an identifier,
a filename. "This is important" is not a reason. If the description only
restates the text, drop it and write a better text. This line is the only
evidence on the surface — a feed row carries no link to the work behind it.

**`--source-label`** is the place the reader would go looking: the topic
(`"staging certificates"`), never the name of the job that found it.

## Examples

Something worth knowing, nothing to decide — a note:

```bash
heliox feed note --to @alice \
  --text "eu-west-1 RDS maintenance Sunday 02:00-04:00; nothing needs to move" \
  --source-label "AWS maintenance"
```

One decision, with the fact the verdict turns on as its reason — a suggestion:

```bash
heliox feed suggest --to @alice \
  --text "Chase the unpaid Meridian invoice before Friday" \
  --description "3 payment retries exhausted, 1840 USD outstanding; the account auto-suspends Friday." \
  --source-label "Meridian billing"
```

A piece of work that surfaced several things — several rows in one call, the
flags repeating in step:

```bash
heliox feed suggest --to @alice \
  --text "Assign an owner for the flaky payments e2e suite" \
  --description "4 of the last 5 nightly runs failed on the same two tests; nobody is on it." \
  --source-label "payments e2e" \
  --text "Approve dropping the legacy /v1/orders endpoint" \
  --description "Zero traffic for 30 days; its deprecation window ended Monday." \
  --source-label "orders API"
```

The repeated flags line up by position, and the rule is **none or all**: give
`--description` (or `--source-label`) either zero times or exactly once per
`--text` — any other count is refused, not paired off. An item with no reason
takes `--description ""` to hold its position. A push carries at most 10
items; more than that is not a feed set, it is a report.

**The shape to avoid** is one row whose body is a list. Every line you would
caption "needs your call" is its own suggestion; a decision buried inside a
note's body cannot be accepted, so the reader has to retype it somewhere else
to act on it. The rest of what you found belongs where the work is recorded
(the run's thread, or your reply in the conversation), with at most a short
note on top.

## The ladder

Pick **per finding** — never per run, per errand, or per report — the
quietest rung that still does the job:

| | When |
| --- | --- |
| say nothing (in a run, that verb is `heliox automation run skip`) | nothing changed; the world is as they already believe it is |
| `heliox feed note` | something changed or was announced, even if no action is needed |
| `heliox feed suggest` | you want a decision |
| `heliox feed suggest` an automation | the work in your hands names a future moment, or is repeating — the clock is itself a finding (§Suggesting an automation below) |
| `heliox message send` | it really must interrupt them right now |

The line between the first two is whether their picture of the world is now
wrong: a scheduled maintenance window or a breaking-change notice IS a note —
"no action needed" is not "not worth knowing". A digest nobody has to act on
is a note, not a DM. A run that broke still DMs the owner — someone whose
automation failed should be interrupted.

## Suggesting an automation: work that belongs on a clock

An automation is work pinned to TIME instead of to a conversation — either
once ("at 14:00 Thursday, do X") or on a rhythm ("every morning, do X").
Your turn ends when you answer; anything that should happen at a *later
moment* dies with it unless it gets a clock. So whenever the material in
front of you implies work at a later moment, the right move is a suggestion
proposing the clock. Accepting it is the person's authorization, not the
scheduling itself: the accept opens a task, and setting up the automation
inside that task is your first move there.

Two shapes to recognize:

- **The material names a future moment, and work belongs just before it.**
  A meeting on the calendar, a due date on an invoice, an expiry on a cert.
  The moment is in the material; the prep work is implied, and nobody asked
  for it — that is exactly why it is worth suggesting. First occurrence
  counts; there is nothing to wait for.
- **The work repeats.** The same shape a second time (another morning's
  triage, another week's digest), a rhythm word in the ask ("every
  morning", "each Friday"), or a standing watch ("keep an eye on", "let me
  know when"). A repeat belongs on a schedule, not on someone remembering
  to hand it to you.

The row follows the ordinary suggestion rules, plus three of its own: the
CLOCK goes in the row — the moment in the text, where it came from in the
description, stated countably; for a recurring one, check
`heliox automation catalog list` first and name the entry if one already
does this; and raise it BESIDE the work's own rows, never instead of them —
today's work still gets delivered today. Same verdict rule as every row:
propose once; dismissed means it stays manual, and you don't re-raise it.

A meeting invite in the inbox — the moment is Thursday 15:00, the implied
work is the prep:

```bash
heliox feed suggest --to @alice \
  --text "Before Thursday's 15:00 client meeting, pull together the Zhang account materials" \
  --description "Meeting invite landed in this morning's inbox; the materials don't exist yet." \
  --source-label "client meeting prep"
```

The same triage handed over two mornings in a row — the evidence is the
count, and the catalog already has a fit:

```bash
heliox feed suggest --to @alice \
  --text "Put the morning inbox triage on autopilot" \
  --description "Second morning in a row handed to me by hand; the @helio/daily-priorities catalog entry covers this." \
  --source-label "morning triage"
```

## Before you deliver: look

`heliox feed list --to @alice` shows what is already on their Home: every
agent-raised row — yours and other teammates' — plus what the person accepted
or dismissed in the last 30 days. Decide per row, then act:

| You see | You do |
| --- | --- |
| a row that still says the right thing | leave it |
| your pending row, wording or reason now stale | `heliox feed update <id> --text ... --description ...` |
| your pending row, no longer worth their attention | `heliox feed withdraw <id>` |
| something they dismissed that you were about to raise again | don't — unless the thing itself changed |
| a teammate already raised the same thing | don't raise it twice |
| a genuinely new finding | push it |
| the desk already piled high with pending rows | clear or revise before adding — a full desk refuses pushes |

Whether a new finding IS one of the rows you see — reworded, narrowed, half
overlapping — is **your** judgment. No server rule matches them for you, and
none protects the person from being asked twice. That protection is you
looking first.

Two mechanics to know:

- **An update restates the whole item.** Pass all three lines as they should
  now read; an omitted `--description` or `--source-label` clears the stored
  one. The row keeps its place — same id, no jump on their Home.
- **Pushing again ADDS rows.** There is no server-side convergence: a blind
  retry after a failed push duplicates. Recover by looking, not re-sending.

## What the server does hold

- **A closed row is immutable.** Once the person accepts or dismisses, the
  row is theirs: update and withdraw refuse it, and nothing reopens it. If a
  correction really must reach them after a verdict, `heliox message send`.
- **You touch only what you raised.** Other agents' rows show in `list` so
  you don't duplicate them; they are not yours to edit.
- **A desk holds at most 30 pending rows.** A push that would carry someone's
  Home past that is refused whole (409). The refusal means the person is
  behind, not that you should retry: run the loop above — look, withdraw what
  no longer earns its place, then push.
- **Inside an automation run**, accepting a suggestion binds to this run's
  thread, so the person lands where the context already is. That binding is
  stamped from the run automatically; there is no flag for it.

A `success` run must have delivered to every subscriber, and a feed push
counts as that delivery — the question is whether the person heard, not which
door carried it. A `failed` run still DMs its owner regardless: that message
exists to interrupt, and feed is the door that does not. A `skip` run pushes
nothing at all.

## Traps

- **Prose split by the shell is refused, not truncated.** The push verbs take
  no positional; quote `--text` and `--description`, and if the body carries
  `$` or backticks, write the invocation as a JSON array and run
  `heliox --args-file <path>`.
- **All-or-nothing on the names, not on the writes.** The recipient list is
  checked in full before the first item lands, but the fan-out is not atomic.
  If a push fails partway, `heliox feed list` tells you what landed.
- **`update` with only `--text` clears the description.** It restates the
  whole item — pass every line you want to keep.
- **Withdrawing removes the row outright.** It was never judged, so nothing
  of it is kept; don't withdraw what you might restate a minute later —
  update it instead.
- **`feed list` answering 404 means an older server.** The management verbs
  are newer than the push; on a server that predates them, skip the look and
  push — delivery must not be what the look-first loop blocks.
