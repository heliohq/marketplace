---
name: feed
description: "Use after substantive work or an automation result when new evidence may warrant a non-urgent update a person should see later, or one distinct task you can perform after they accept it. Trigger on meaningful state changes, requested or subscribed digests, unassigned AI-executable follow-ups, and repeatable work; skip current-turn work, urgent risks, routine success without a delivery obligation, human-only decisions, and work already owned or underway."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox feed --help"
---

# Heliox Feed

Feed rows appear on a person's Home as durable attention, not as a transcript of
what an agent noticed or a generic list of next steps.

- A **note** states a meaningful new condition or result. It asks nothing and
  expires after 24 hours.
- A **suggestion** offers one new piece of work that you, the proposing AI
  teammate, can perform. Acceptance creates a task assigned to the row's
  author; dismissal creates nothing.

Only people have Home. Never address a feed row to an AI teammate.

Keep four decisions separate: finish the requested work, satisfy this turn's
delivery obligations, decide whether anything deserves durable attention, and
then reconcile existing rows before writing. One decision never substitutes for
another.

## 1. Finish the work already authorized

First deliver what the person asked for, within the available evidence. A Home
suggestion must not postpone, repackage, or replace work that belongs in the
current turn.

If asked to prepare today's agenda, prepare it now. Do not suggest `Prepare
today's agenda`. A separate suggestion is possible only when the work exposes a
different, independently acceptable task that was not already authorized.

Deliver the finished work itself. A link plus “I wrote it,” commentary about
drafting choices, or a request for more inputs does not replace the requested
memo, email, table, correction, or agenda. When evidence is incomplete, produce
the best complete shape available and mark the missing fields as unknown. Keep
every requested section or row visible; missing evidence is a value to label,
not a reason to omit part of the deliverable.

Then scan the finished work for separate candidates. The recurring patterns are:

- a concrete mismatch between records or between an expected item and the
  authoritative batch;
- an external request that still lacks an answer;
- a stale dependency whose owner is known but whose needed status or outcome is
  not being followed up;
- a repeated manual step that could produce a useful recurring outcome.

Mentioning one of these in the requested report does not assign or track it. It
may still be a separate Home suggestion when it passes the gates below.

## 2. Satisfy this turn's delivery obligations

Delivery is about whether a person was reached in the current turn. Existing
Feed state is about what remains useful across turns. An old pending row never
proves that the current turn delivered anything.

| Obligation | Required delivery |
| --- | --- |
| Waiting could cause security exposure, data loss, financial loss, an outage, or a missed deadline | Send an urgent message or say it directly now |
| The person already authorized work in this turn | Do the work now and deliver the result |
| Requested or subscribed successful automation result | Post the full result in the run thread and make one current-turn delivery to every subscriber |
| Failed automation run | Post the failure in the run thread and message the owner; a Feed row is not enough |
| Rehearsal, or routine success with no requested or subscribed delivery | Keep the result in the run thread; no recipient delivery is required |

For a successful non-rehearsal automation, the run thread is the permanent audit
record. Subscriber delivery is a separate leg and must produce a covering action
in this turn. The runtime recognizes `feed note`, `feed suggest`, `feed update`,
or a message, but the route still has to match the content: a result is normally
a note or update, while a suggestion must independently pass every gate below.
If the same recurring result is already represented by an older pending row,
either revise or replace your row when that is the truthful lifecycle action,
or use another covering delivery. Never finalize the run on the strength of the
old row alone.

Keep facts and recommendations required by a requested report, document, table,
or other artifact inside that deliverable. Artifact content is not a duplicate
notification. Likewise, the automation run thread remains required audit even
when Feed delivers the digest.

Outside required artifact content and the run audit, use one user-facing
notification for the same fact or commission. After a successful Feed write, do
not repeat its wording in a conversational reply. Send a separate message only
when urgency or an explicit conversational request calls for it.

Before treating Feed as that user-facing notification, inspect
`heliox me show --json`. Feed is visible only when `feature_flags.suggestions`
is `true`, or during the active first-build flow when
`feature_flags.onboarding_v6` is `true` and its Suggestions screen is the
delivery surface. If neither condition holds or the flags are unavailable, do
not treat a successful Feed write as delivery: send the result by message or in
the current reply instead. An invisible row cannot cover an automation
subscriber.

## 3. Decide what should remain visible

| Situation | Route |
| --- | --- |
| A meaningful non-urgent state changed and no response is needed | `feed note` |
| A distinct, non-urgent AI task passes every suggestion gate below | `feed suggest` |
| A useful recurring, scheduled, event-triggered, or monitored job should be set up | Propose setup with `feed suggest` |
| A requested or subscribed result can wait | Deliver it with `feed note` to each recipient not already reached in this turn |
| Routine success with no delivery obligation, unchanged status, intermediate findings, weak speculation, or work already covered | Keep Home quiet |

A note has no hidden request. A suggestion offers work that starts only after
acceptance. The correct outcome is often no row.

## 4. Reconcile existing rows before writing

Identify the person who can accept the commission, then run
`heliox feed list --to @handle` before creating, updating, or withdrawing a row.
The current speaker is not automatically that person. Inspect the Home of the
known decision owner when the work belongs to them.

The list is desk-wide. In text output, `(yours)` marks a row you raised; in JSON,
only `mine: true` means the same thing. Run `feed update` or `feed withdraw` only
for a row marked `(yours)` or `mine: true`. `mine: false` is another agent's row,
and the presence of the field does not grant ownership. The list does not
identify that row's author.

Compare by meaning, not exact wording. A later conversation with somebody else
does not transfer an existing decision or justify a second row. Preserve the
original recipient unless evidence explicitly changes ownership.

Before creating from a cross-person interaction, check every established human
decision owner's Home for the same work. Check the current speaker's Home too
only when the speaker is a person and may be the owner or recipient. An AI
speaker has no Home, so never run `feed list` against their handle. If ownership
cannot be established, do not use the current speaker as a fallback recipient
and do not create until the relevant human's Home has been checked.

| Existing state | Action |
| --- | --- |
| Pending suggestion is still the same accurate commission | Leave it unchanged |
| Pending note still represents the same observation and this turn has no new delivery obligation | Leave it unchanged |
| Your pending suggestion is the same work but its scope or evidence changed, including when only part remains | `feed update` |
| Your pending note needs only a wording or provenance correction for the same observation | `feed update`; its original expiry keeps ticking |
| Your pending note now represents a new condition or result that deserves a fresh 24-hour visibility window | `feed withdraw`, then create the new note |
| A subscribed automation produced a new run of the same result | Satisfy current-turn delivery; when Feed is the route, treat the run as a fresh result rather than relying on the old row |
| Your pending row is complete, assigned elsewhere, or no longer useful | `feed withdraw` |
| Another agent already raised the same work and the row is still accurate | Leave it unchanged and do not duplicate it |
| Another agent's row is stale or complete | Do not update, withdraw, or duplicate it. If context identifies the author, ask them to reconcile it; otherwise leave it unchanged |
| The person dismissed the same unchanged proposal | Do not raise it again |
| No existing row represents the genuinely new work or state | Create the note or suggestion chosen in step 3 |

Conversation does not reconcile Home. If the final delivery says something is
closed, cleared, assigned, or resolved, reconcile your own stale row first and
use the non-mutating path above for another agent's row. Withdrawal says no
useful commission remains. When one exception or narrower follow-up is still
open, narrow your existing suggestion instead of closing it.

Reading a person's Home does not widen the audience for its contents. Never
quote, summarize, or confirm a row to a different current speaker. If its author
cannot be reached, leave the row unchanged rather than disclosing it elsewhere.

## The suggestion gates

A suggestion must pass all five gates:

1. **Separate** — it is not already part of the current authorization.
2. **Commissionable** — you can personally carry the work forward and return an
   observable result. Acceptance assigns the task to you because you authored
   the row; do not offer work for a different AI teammate.
3. **Supported gap** — the source establishes an unmet outcome, missing required
   input, unanswered request, or record discrepancy. The gap is not merely an
   unsuccessful search or the absence of a stronger status.
4. **Not duplicated** — the same AI deliverable or follow-up is not already
   assigned, tracked, or underway.
5. **Durable** — it is important but non-urgent and worth occupying Home until
   the person accepts or dismisses it.

Use this sentence test:

> After acceptance, I will **[do what]** and return **[what verifiable
> result]**.

If that sentence cannot be completed honestly, do not create the suggestion.

### Offer work you can execute, not human homework

`Approve the launch`, `Choose a vendor`, `Enter bank details`, and `Find an
owner` are human decisions or sensitive human actions, not AI commissions. Keep
the decision visible in the requested deliverable or conversation.

When useful and genuinely separate, propose the AI contribution that reduces
the human decision: investigate, compare, draft, reconcile, coordinate, verify,
or prepare a decision-ready packet. Do not merely put an AI verb in front of a
human decision.

| Do not suggest | A commissionable alternative, when supported |
| --- | --- |
| `Choose who owns the renewal` | `Compare renewal usage and cost, then return a decision-ready brief` |
| `确定退款由谁负责` | `核对未处理退款并整理需要财务确认的清单` |

The alternative still has to pass the other gates. Do not manufacture a brief,
investigation, or follow-up only to create a suggestion.

If a different AI teammate should do the work, coordinate or hand it off on the
current collaboration surface. Do not raise the suggestion under your name:
acceptance cannot transfer the resulting task to another AI.

A person may own the underlying dependency while the coordination outcome is
still unclaimed. If a contract team owns a review but nobody is tracking the
answer needed for a milestone, `Follow up on the review and return approval or
remaining blockers` is different work. It becomes a duplicate only when that
same follow-up and result are already assigned or tracked.

### Treat evidence as the ceiling

Use explicit source evidence for dates, numbers, owners, status, and causality.

- Preserve the status and workflow stage the source gives. `requested` is not
  `promised` and `scheduled` is not `shipped`. Evidence about one stage neither
  proves a later stage is complete nor establishes that the later stage is a
  current requirement.
- A missing search result means unknown, not absent. Failing to find an owner,
  file, date, or person does not prove none exists.
- An explicit mismatch or missing required record can establish work even when
  the source does not say “unowned.” Do not add that ownership claim to the row.
- A known owner or tracker for the same proposed result means it is already
  covered, even when incomplete. An owner of an underlying dependency does not
  automatically cover a separate follow-up or coordination result.
- Write `only`, `blocked`, `will miss`, or a named cause only when the evidence
  establishes it.
- Recalculate summaries from supported components. If a total includes several
  components or one component is unquantified, report the observable lines
  instead of attributing the whole total to one cause.
- Your own draft, promise, deadline, success criterion, or follow-up plan is not
  source evidence. Never justify a row with what “your reply promises.”

Phrase the work around what the AI teammate will deliver, not around the missing
human or the absence of information.

## Automation is a suggestion, not a side comment

When real work reveals a repeatable cadence, propose the recurring outcome on
Home instead of appending “Would you like me to automate this?” to the reply.

Before proposing it, read `heliox:automation-creator`, inspect the automation
catalog, and check the person's existing automations. Acceptance starts setup;
it does not create or enable the automation in advance.

| Field | English | 中文 |
| --- | --- | --- |
| text | `Set up a Friday inventory exception brief` | `设置每周五自动整理库存异常` |
| description | `The same warehouse check and summary is needed before each review.` | `每次周会前都要检查同一批仓库数据并整理变化。` |
| source label | `inventory review` | `库存周会` |

## Write a row that can stand alone

One suggestion contains one independently acceptable task. One note contains
one state change or result. If a person could accept A and dismiss B, create two
suggestions. Do not create one row per log line, metric, or intermediate finding.

| Field | Contract |
| --- | --- |
| suggestion `--text` | Concrete AI-owned work and outcome; becomes the task title |
| note `--text` | New state or result, stated first |
| `--description` | One useful reason: evidence, consequence, blocker, or deadline |
| `--source-label` | The system, project, account, artifact, or event the person would recognize |
| `--source-provider` | Exact integration catalog key only when one known integration directly produced the row |

Prefer no more than 60 characters for suggestion text, 70 for note text, and
120 for description. The CLI's 80-character text and 140-character description
limits are hard ceilings, not writing targets. Suggestion text becomes a
single-line task title after acceptance, so put the distinguishing object and
outcome before detail that may be truncated.

Text must name the specific object; description should add information rather
than paraphrase the title. Omit a description that adds nothing. A person
scanning the title alone should recognize the account, project, system, or
artifact; source label and description do not rescue a vague title.

Write Chinese as Chinese, not translated English. Prefer a specific object,
state, time, and action. Remove filler such as `基于以上分析`, `值得注意的是`,
`可以考虑`, `建议您及时`, `相关`, and `进行处理`.

| Avoid | Write |
| --- | --- |
| `基于以上分析，建议您及时处理报表系统令牌的更换问题` | `明早前更换报表系统令牌` |
| `值得注意的是，维护期间用户可能会经历一次连接中断` | `维护期间，已登录用户可能会短暂断线一次` |

Use `--source-provider` only for direct single-integration provenance, with an
exact key such as `github`, `google_calendar`, `microsoft_outlook`, or `gmail`.
Omit it for Helio-generated, automation-generated, mixed-source, or uncertain
rows. The human-readable `--source-label` still carries the useful context.

## Decision examples

Examples teach decisions, not reusable wording. Do not copy their nouns,
claims, or sentence frames into unrelated work. Write Chinese directly rather
than translating line by line.

- **Current work versus new work:** deliver a requested lease comparison now;
  do not suggest `Prepare the lease comparison` / `整理租赁方案对比`. If the
  source separately flags unreviewed insurance clauses required before
  signature, `Review the lease's insurance terms and return open risks` /
  `核对租约中的保险条款，整理尚未解决的风险` is a different commission.
- **Human decision versus AI contribution:** do not suggest `Choose the research
  vendor` / `决定用哪家调研供应商`. When two proposals use different assumptions,
  suggest `Normalize the vendor proposals and prepare a decision table` /
  `统一两家供应商的报价口径，整理选型表`.
- **Different AI executor:** do not suggest `Have the research teammate audit
  the interview notes` / `让调研同事核对访谈记录` under your name. Hand the work
  to that teammate on the collaboration surface; Home acceptance cannot reassign
  your row.

| Evidence | Decision |
| --- | --- |
| The quarterly access review explicitly says the audit packet is incomplete and unowned | Suggest `Compile the access-review evidence and flag missing attestations` / `整理权限审查材料，标出缺少的确认记录` |
| The payment register shows approved invoices absent from the next payment batch | Suggest reconciling the missing invoices and returning a payment-ready list; reporting the mismatch alone does not track it |
| Search did not find a supplier checklist or its named author, but the user says the author is drafting it | Report the retrieval limit if relevant; do not claim the author or owner is absent |
| The finance tracker says Siyu is already reconciling seven disputed refunds | Keep Home quiet; incomplete work already has an owner and tracker |

A green result stays green. Treat the current result as authoritative unless it
explicitly names a separate failure or unmet requirement. Do not revive an
earlier concern or replace a satisfied criterion with a stricter downstream
criterion that the source never required.

For a non-action state, use a note rather than disguised work:

| Field | English | 中文 |
| --- | --- | --- |
| text | `Payroll portal maintenance: Sunday 02:00-04:00` | `工资系统周日 02:00 至 04:00 维护` |
| description | `Employees may need to sign in again afterward.` | `维护结束后，员工可能需要重新登录。` |
| source label | `payroll portal maintenance` | `工资系统维护` |

When an existing suggestion compares three vendors and one withdraws, update it
to two rather than stacking another row. Once procurement records its choice,
withdraw the row before reporting completion.

## Final check

Before the final send or cede, audit both the requested work and Feed copy. Trace
every date, number, owner, status, cause, deadline, and commitment to source
evidence; remove unsupported claims rather than making them sound cautious. If
an artifact was already drafted, inspect and correct it before delivery. Keep
required findings in that artifact and required automation results in the run
thread. Avoid only duplicate user-facing notifications: once Feed delivers a
fact or commission, do not restate the same notification in another channel or
the final reply unless urgency or an explicit request requires it.

## Run the commands

```bash
heliox feed list --to @alice

heliox feed suggest --to @alice \
  --text "Reconcile invoice #4471 and prepare its payment packet" \
  --description "The supplier disputed the tax amount; Finance needs a corrected packet." \
  --source-label "Northwind invoice #4471"

heliox feed note --to @alice \
  --text "GitHub deployment checks failed on main" \
  --source-label "atlas/widgets · main" \
  --source-provider github

heliox feed update <id> \
  --text "Reconcile invoice #4471 and prepare its payment packet" \
  --description "The corrected invoice is due Monday." \
  --source-label "Northwind invoice #4471"

heliox feed withdraw <id>
```

`update` restates the whole row. Pass every field that should remain; omitting
`--description`, `--source-label`, or `--source-provider` clears it. Accepted or
dismissed rows cannot change, and an agent can update or withdraw only its own
pending rows.

For a batch, repeat `--text`, `--description`, `--source-label`, and
`--source-provider` in matching order. Supply each optional flag either zero
times or once per text; use an empty string to preserve a position. A push can
carry at most 10 rows. Larger sets belong in a report or digest.

A new push always adds rows; the server does not merge duplicates. If a write
may have partially succeeded, list every recipient before retrying. If the desk
returns 409 at its pending-row limit, revise or withdraw stale rows before
adding more.

Quote all prose flags. If text, description, or source label contains `$` or
backticks, put the invocation in a JSON array and run it with
`heliox --args-file <path>` on the first attempt.
