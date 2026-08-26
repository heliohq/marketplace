---
name: feed
description: "Use this skill for `heliox feed` whenever completed work, a new condition, a requested digest, or a proposed next step might belong on a person's Helio Home. It chooses the route: no feed item, a non-urgent note that needs no response, one action that starts after acceptance, recurring or scheduled work, or an urgent message instead. It then writes compact text, description, and source label. Routine success stays in the run, and AI teammates do not receive Home items."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox feed --help"
---

# Heliox Feed

## Purpose

Feed places non-urgent information and proposed work on a person's Home. A row
can show `--text`, `--description`, and `--source-label`.

- `note` states a new condition that needs no response. It expires after 24
  hours.
- `suggest` proposes one action. Accepting it creates a task; dismissing it
  creates nothing.

An agent can propose work but cannot add work directly to another person's
task list. Recipients must be people; AI teammates do not have Home.

## Decide before writing

Make these decisions in order. They are separate decisions, not a ladder.

### 1. Does this belong on Home?

Write a feed row only when at least one condition is true:

- A new fact changes the recipient's plan, deadline, access, cost, risk, or
  ownership.
- The recipient asked for this result or digest on Home.
- The recipient must authorize a specific action.

Keep routine completion, healthy checks, unchanged status, investigation
steps, discarded theories, and supporting evidence in the run or conversation.
If none of the three conditions is true, do not call `heliox feed`.

Skip the row when there is evidence the recipient already received the same fact. Another person owning the action does not remove the recipient's need to know; the result may still deserve a note.

### 2. Can it wait for the next Home visit?

Use `heliox message send` when waiting could cause an outage, missed deadline,
security exposure, data loss, or financial loss. A failed automation run still
messages its owner. Feed is for information that can wait.

### 3. Does acceptance start work?

| Result | Row |
| --- | --- |
| The recipient only needs the new state | `heliox feed note` |
| The recipient must authorize one action | `heliox feed suggest` |

A note contains no hidden request. A suggestion names the work that starts
after acceptance.

### 4. Should the work run later as an automation?

Automation is a task type, not a reason to appear on Home. Apply the Home test
above first. Propose one only when the evidence shows a future trigger or a
repeated need.

Before proposing one, read `heliox:automation-creator` for the current
capabilities and creation flow. Use an automation when AI work should run from
one of these triggers:

- a named future moment, including a one-time reminder;
- a recurring cadence;
- an event or monitored condition.

Separate a deadline from a trigger. `File the permit by Wednesday` is a normal
suggestion because acceptance starts the work now. `Remind me Wednesday to file
the permit` is an automation because Wednesday starts future AI work. If the
work can and should be completed now, do not defer it to an automation.

Check `heliox automation catalog list` and `heliox automation list --json`
before writing the suggestion. Reuse a matching catalog procedure, or refine a
matching automation instead of creating a duplicate. Propose the setup or
refinement rather than one execution. Name the trigger and result so acceptance
starts a concrete task. Do not create or enable the automation before the
recipient accepts.

## Define one row

- One suggestion contains one independently acceptable action. If the person
  could accept A and dismiss B, write two suggestions.
- One note contains one state change or one completed result. Related facts
  can share a note only when they have the same consequence.
- Do not create one note per log line, metric, or finding.
- A requested digest can be one note. Put its details in the run or digest,
  not in the Home row.

## Write the fields

| Field | Contract |
| --- | --- |
| suggestion `--text` | work that starts after acceptance; 60 characters or fewer |
| note `--text` | new state or outcome; 70 characters or fewer |
| `--description` | one decision reason: context plus the blocker, consequence, deadline, or evidence; 120 characters or fewer |
| `--source-label` | concrete system, project, account, or event |

The server limits are safety ceilings. They are not writing targets.

Read `--text` by itself before writing. It must name the specific project,
account, system, customer, event, or artifact. A version number, deadline,
owner, or generic noun such as `release`, `report`, or `credential` does not
identify the subject when it could refer to more than one thing. Description
and source label add context; they cannot supply a subject missing from text.

### Suggestion text

Use **concrete verb + object + optional deadline**. The title becomes the task
title after acceptance.

Acceptance already means yes. Write the action that starts after acceptance.
Convert a `whether` clause or an `either/or` choice into the single action
supported by the evidence:

| Input framing | Suggestion title |
| --- | --- |
| `Approve renewing the contract` | `Renew the contract` |
| `Review whether to replace the expired credential` | `Replace the expired credential` |
| `Assign the on-call lead or leave the queue unowned` | `Assign the on-call lead to the support queue` |

Use a verb that names observable work. Replace abstract verbs such as `address`,
`handle`, `improve`, `optimize`, `enhance`, `ensure`, `support`, `drive`, or
`look into` with the action they stand for. `Review PR #482` is valid because
producing the review is the work. If the evidence does not support one action,
keep the decision in the run and raise no suggestion.

### Note text

State the result first. Name the system or event and its new state. Do not add
`FYI`, `Please note`, `Update`, `I found`, or `Good news`.

A routine success is not a note unless the recipient asked for that result or
the success changes one of the Home conditions above.

### Description

Omit `--description` when the text alone gives enough context to understand the
state or accept the action. Otherwise write the smallest complete reason the
recipient needs: what is blocked, what consequence follows, which deadline
changes the decision, or what evidence makes the action worth accepting.

Give the fields different jobs. Text says **what changed** or **what work starts**;
description says **why it matters now**. After drafting both, compare them fact by
fact. Remove any description clause that only paraphrases an action, state,
deadline, or measurement already in text. Repeating the subject name is allowed
when clarity requires it; repeating the same decision fact is not. If nothing new
remains, omit `--description`.

One reason may join two facts when they form one causal point, such as a
condition and its direct consequence or a measurement and its comparison. Keep
both when dropping either would leave the recipient asking why the row matters.
Do not add a second reason merely because more evidence is available; leave
supporting details in the run or digest.

Do not include investigation history, correction history, process narration,
lists, repeated title text, or a second recommendation. Replace unsupported
adjectives such as `important`, `critical`, `significant`, `major`, and
`urgent` with the number, deadline, or consequence that proves the claim.

| Text | Avoid this description | Write this instead |
| --- | --- | --- |
| `Renew the vendor contract by Friday` | `The contract must be renewed by Friday because access ends Monday.` | `Access ends Monday without renewal.` |
| `The nightly backup missed its window` | `The nightly backup did not run on time.` | `The latest recovery point is now 18 hours old.` |

### Source label

Use the name the recipient would search for: `vendor contract`, `support queue`,
or `service maintenance`. Do not use the automation name or generic labels
such as `update`, `task`, `finding`, or `review`.

### Remove filler

Delete every word that does not name the action, object, owner, date, amount,
count, state, or consequence. Do not write stock phrases such as `Based on the
analysis`, `It may be worth`, `moving forward`, `in order to`, `proactively`,
`comprehensive`, `seamless`, or `leverage`.

## General examples

These examples teach the routing rule. Adapt the nouns and facts to the actual
work.

### Expected result

Input: A scheduled check completed as expected, no alert remains, and nobody
requested a Home digest.

Output: no feed row.

### New state with no action

Input: A service maintenance window was announced for Sunday from 02:00 to
04:00. Active sessions will reconnect once. The recipient needs no action.

Output:

- kind: `note`
- text: `Maintenance is scheduled for Sunday 02:00-04:00`
- description: `Active sessions will reconnect once.`
- source label: `service maintenance`

### One authorized action

Input: A vendor contract expires Friday. Access ends Monday without renewal,
which requires the recipient's approval.

Output:

- kind: `suggest`
- text: `Renew the vendor contract by Friday`
- description: `Access ends Monday without renewal.`
- source label: `vendor contract`

### One-time work and automated work

| Input | Route | Text |
| --- | --- | --- |
| A permit application must be filed once by Wednesday | normal suggestion | `File the permit application by Wednesday` |
| The person needs a reminder on Wednesday to file it | automation suggestion | `Schedule a Wednesday permit reminder` |
| The same inventory count is needed every Monday | automation suggestion | `Automate the Monday inventory count` |
| A payment failure should notify the finance team | automation suggestion | `Notify Finance when a payment fails` |

### CLI shape

Use one command after choosing the route and fields:

```bash
heliox feed suggest --to @alice \
  --text "Renew the vendor contract by Friday" \
  --description "Access ends Monday without renewal." \
  --source-label "vendor contract"
```

## Batch rows

Repeat `--text`, `--description`, and `--source-label` in matching order. For
each optional flag, provide it zero times or once per text. Use an empty string
to hold the position of a row that needs no description or source label.

A push carries at most 10 rows. More than 10 rows belongs in a report or
digest.

## Check Home before writing

Run `heliox feed list --to @alice` before adding or changing rows. It shows
pending rows from every agent and accepted or dismissed rows from the last 30
days.

| Existing state | Action |
| --- | --- |
| The pending row is accurate | leave it |
| Your pending row has stale text or evidence | `heliox feed update <id>` |
| Your pending row no longer deserves attention | `heliox feed withdraw <id>` |
| The person dismissed the same unchanged proposal | do not raise it again |
| Another agent raised the same item | do not duplicate it |
| The fact or proposed work is new | create the row |

Judge identity by meaning, not exact wording. If a push may have failed after
writing some recipients, list the rows before retrying.

## Command behavior

- `update` restates the entire row. Pass every field that should remain; an
  omitted `--description` or `--source-label` clears it.
- A new push always adds rows. The server does not merge duplicates.
- Accepted and dismissed rows cannot be updated or withdrawn.
- An agent can update or withdraw only rows it created.
- A Home can hold at most 30 pending rows. If a push returns 409, revise or
  withdraw stale rows before adding more.
- In an automation run, accepting a suggestion binds the task to that run's
  thread.
- A successful feed push counts as subscriber delivery. A failed automation
  run still requires a message to its owner. A skipped run pushes nothing.

## Shell and compatibility rules

- Quote `--text` and `--description`. If either contains `$` or backticks, put
  the invocation in a JSON array and use `heliox --args-file <path>`. Choose
  this form before the first write; do not attempt a raw invocation and retry.
- Recipient names are checked before the first write, but fan-out is not
  atomic. After a partial failure, list rows before retrying.
- `feed list` returning 404 means the server predates the management commands.
  On that server, skip the look step and use the push command.
