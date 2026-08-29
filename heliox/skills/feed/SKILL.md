---
name: feed
description: "Use this skill for `heliox feed` whenever completed work, a new condition, a requested digest, or a proposed next step might belong on a person's Helio Home. It chooses the route: no feed item, a non-urgent note that needs no response, one action that starts after acceptance, recurring or scheduled work, or an urgent message instead. It then writes compact text, description, source label, and optional single-integration icon metadata. Routine success stays in the run, and AI teammates do not receive Home items."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox feed --help"
---

# Heliox Feed

Feed places non-urgent information and proposed work on a person's Home.

- `note` states a new condition that needs no response and expires after 24
  hours.
- `suggest` proposes one action. Accepting it creates a task; dismissing it
  creates nothing.

Agents propose; people decide. Recipients must be people because AI teammates
do not have Home.

## Decide before writing

Write a feed row only when at least one condition is true:

- A new fact changes the recipient's plan, deadline, access, cost, risk, or
  ownership.
- The recipient asked for this result or digest on Home.
- The recipient must authorize a specific action.

Keep routine completion, healthy checks, unchanged status, investigation
steps, discarded theories, and supporting evidence in the run or conversation.
Do not repeat a fact the recipient already received.

Use `heliox message send` when waiting could cause an outage, missed deadline,
security exposure, data loss, or financial loss. A failed automation run still
messages its owner. Feed is for information that can wait.

| Result | Row |
| --- | --- |
| The recipient only needs the new state | `heliox feed note` |
| The recipient must authorize one action | `heliox feed suggest` |

A note contains no hidden request. A suggestion names the work that starts
after acceptance.

For future, recurring, event-triggered, or monitored work, read
`heliox:automation-creator`. Check the automation catalog and the person's
existing automations before proposing setup or refinement. Do not create or
enable it before acceptance.

## Define one row

- One suggestion contains one independently acceptable action. If the person
  could accept A and dismiss B, write two suggestions.
- One note contains one state change or completed result. Related facts can
  share a note only when they have the same consequence.
- Do not create one note per log line, metric, or finding.
- A requested digest can be one note; keep its detail in the digest.

## Write the fields

| Field | Contract |
| --- | --- |
| suggestion `--text` | work that starts after acceptance |
| note `--text` | new state or outcome |
| `--description` | one decision reason: blocker, consequence, deadline, or evidence |
| `--source-label` | concrete system, project, account, or event |
| `--source-provider` | exact integration catalog key when one known integration directly produced the row |

The CLI caps new-row `--text` at 80 characters and `--description` at 140.
Treat those as ceilings, not targets. Text must stand alone and name the
specific system, customer, project, event, or artifact.

- Suggestion text: **concrete verb + object + optional deadline**. It becomes
  the task title after acceptance.
- Note text: state the result first and name the system or event. Do not prefix
  it with `FYI`, `Update`, or process narration.
- Description: add one reason the title does not already say. Omit it when it
  only paraphrases text.
- Source label: use the place or object the recipient would search for, not an
  automation name or a generic label such as `finding` or `review`.

`feed update` accepts the wider server limits so an existing row can be
restated without truncation.

### Source provider

Use `--source-provider` only when the row directly originates from one known
integration. Pass its exact catalog key, such as `github`, `google_calendar`,
`microsoft_outlook`, or `gmail`.

Omit it for Helio-generated, Automation-generated, mixed-source, and uncertain
rows. Do not derive it from the source label, channel name, automation name, or
the icon you expect to see.

`--source-label` remains the human-readable provenance line. The provider key
only selects a bundled brand icon; it does not prove authorization, create a
link, or replace the label. Unknown keys safely use the semantic fallback icon.

## Examples

Routine success with no requested digest produces no feed row.

```bash
heliox feed suggest --to @alice \
  --text "Renew the vendor contract by Friday" \
  --description "Access ends Monday without renewal." \
  --source-label "vendor contract"
```

When a row directly originates from one integration, add its catalog key:

```bash
heliox feed note --to @alice \
  --text "GitHub deployment checks failed on main" \
  --source-label "acme/widgets · main" \
  --source-provider github
```

## Batch rows

Repeat `--text`, `--description`, `--source-label`, and `--source-provider` in
matching order. For each optional flag, provide it zero times or once per text.
Use an empty string to hold the position of a row that needs no value for that
flag.

A push carries at most 10 rows. Put larger sets in a report or digest.

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
  omitted `--description`, `--source-label`, or `--source-provider` clears it.
- A new push always adds rows. The server does not merge duplicates.
- Accepted and dismissed rows cannot be updated or withdrawn.
- An agent can update or withdraw only rows it created.
- If a push returns 409 because the desk is full, revise or withdraw stale
  rows before adding more.
- A successful feed push counts as subscriber delivery. A failed automation
  run still requires a message to its owner. A skipped run pushes nothing.

## Shell safety

- Quote `--text`, `--description`, and `--source-label`. If any prose value
  contains `$` or backticks, put the invocation in a JSON array and use
  `heliox --args-file <path>`. Choose this form before the first write; do not
  attempt a raw invocation and retry. `--source-provider` is a structured
  catalog key, not prose.
- Recipients and desk capacities are checked before the insert. A storage
  failure can still be partial, so list every recipient before retrying.
