---
name: automation-creator
description: "Create a Helio automation: AI work that runs later from a schedule, reminder, webhook, or monitored condition. Use whenever the user asks to schedule or automate AI work, send a recurring report or digest, watch or monitor something, notify people when an event happens, or follow up later—even if they never say 'automation'. Do not use for a one-off task to complete now, a human calendar event, or an SOP with no future AI execution. For validating, repairing, or improving an automation that already exists, use automation-refiner instead."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox automation --help"
---

# Heliox Automation Creator

This skill turns a request into an automation — a trigger, a procedure document, and an AI that executes it. Your scope ends at "it exists and the procedure reads back correctly." Validation, rehearsal, and ongoing maintenance belong to `heliox:automation-refiner`.

Creating an automation goes like this:

- Pin down what the user actually wants — what it produces, when it runs, who receives it
- Do the work once, right here in the conversation, and get their sign-off on the real output
- Write down what happens on the paths you did not just see
- Pick the trigger from where the signal comes from
- Create it (disabled) and read the procedure back to confirm it landed
- Hand it over, naming what is still unproven

Work out where the user already is before you start. Three common openings:

1. **If nothing exists yet** — start at step 1. This is the default path.
2. **If the user brought an approved example** — they pasted or described the output they want. The "do the work once" step is already done; align on any gaps, then move straight to step 3.
3. **If installing from the catalog** — catalog automations are installed through the product's Start flow, which forks the template procedure, records provenance, and fires the first run. That path is outside this skill's scope; this skill covers automations built from a conversation.

A note on vocabulary: when talking with the user, say "the steps" instead of "procedure," "who runs it" instead of "executor," and "who gets the results" instead of "subscriber." The internal terms are for your CLI calls, not the conversation.

## 1. Pin down what they want

Four questions drive the rest of the process. Ask them in the conversation (not as a form), and explain why each answer matters:

1. **What should this automation produce?** A summary, a status report, a notification, a document — this sets the shape of the procedure and the output format.
2. **What makes it run?** You should ask for the occasion, not a cron expression — "every Monday morning before standup" or "whenever a new issue is labeled urgent." Converting that into a cron string or a webhook filter is your job, not the user's.
3. **What does the result look like, and who receives it?** This determines the output section of the procedure and whether you need subscribers.
4. **How much proof does this need before it goes live?** Give a one-sentence recommendation with a reason (e.g., "this reads public data and posts to a private channel — a single dry run should be enough") and let the user decide. The depth tiers and the actual validation process belong to `heliox:automation-refiner`; here you just need the user's intent so you can pass it along at handover.

Sensible defaults — state them and only ask about what remains: destination is the current conversation, owner is the person asking, executor is you, no additional subscribers beyond the owner (who receives the result of successful runs and a notice when one fails; quiet runs notify nobody).

Do not create anything until all four questions have answers. A half-understood request becomes a half-correct procedure, and unlike a one-off task, this one will run on its own, repeatedly, without anyone watching.

## 2. Do the work once, here

At creation time you have zero run data. A real output exposes preferences, format issues, and missing context faster than any questionnaire.

Execute the request once in the current conversation. If the real event cannot be produced right now (e.g., the source only updates on weekdays), use a clearly labeled historical example and tell the user it is historical.

Show the output to the user and get their sign-off. Pay attention to what they change — those corrections are constraints that belong in the procedure. If they rephrase a heading, tighten a filter, or drop a column, capture that in the procedure's instructions, not just in this conversation.

If the user brought an approved example or has an existing automation to work from, start there instead of redoing the work.

## 3. Write down the paths you did not see

This is the most important section of the whole process. Step 2 exercised exactly one path: the one where everything worked and data was available. But an automation runs unattended, often at odd hours, and the paths you did not see are the ones that will cause problems. Every procedure needs explicit handling for these four situations.

### Nothing found

A bounded read that returns no results within the time window is a normal outcome — "nothing happened this period" — not an error, and not a reason to widen the search. The procedure should spell out what "nothing found" looks like and what to report.

Bad:
> "If no results are found, try expanding the search window or removing filters."

Good:
> "If no messages match the filter in the last 24 hours, post a one-line summary to #ops-daily: 'No new incidents since yesterday's report.' Do not extend the window or loosen the filter — a quiet period is a valid result."

The key distinction: an empty result from looking at the right window is data, not a malfunction. Dropping filters or paging backwards to force a non-empty result is a bug — it turns a "nothing to report" into a stale or misleading output.

### A step fails

A mid-procedure failure (API error, permission denied, unexpected format) should not silently swallow the error or produce a partial output without flagging it. The procedure should name what counts as a failure and who to notify.

Bad:
> "Handle errors appropriately."

Good:
> "If the GitHub API returns a non-200 status, stop the run, send a DM to the owner with the status code and endpoint, and finalize the run as failed with the reason 'GitHub API error: {status} on {endpoint}'."

### Partial success

Some sources may return data for three out of four channels, or a report may render correctly except for one chart. The procedure should define whether a partial result ships (with a note about what is missing) or counts as a failure.

Bad:
> "If some data sources are unavailable, include whatever data is available."

Good:
> "If one of the three source channels returns an error while the others succeed, include the data from the working channels and add a note at the top: 'Data from #frontend-alerts was unavailable — this report covers the other two channels only.' Finalize as success. If two or more channels fail, finalize as failed and DM the owner with the list of errors."

### The source is unreachable

DNS failures, expired tokens, rate limits, and maintenance windows all look different from "nothing found." The procedure should distinguish "I checked and nothing was there" from "I could not check at all" — and say what to do in the second case (retry? notify? skip?).

Bad:
> "If the source is unavailable, retry later."

Good:
> "If the source returns a connection error or a 5xx status, wait 60 seconds and retry once. If the retry also fails, DM the owner with the error and finalize the run as failed with reason 'Source unreachable: {error}'. Do not produce a partial report from cached data."

When working through these paths with the user, ask concrete questions: "What should happen if the Slack channel has zero messages this week?", "If the GitHub API returns an error halfway through, should the automation stop completely or try to finish with whatever it has?", "If one of your three data sources fails but the other two work, do you want the partial report or nothing?", or "If the API is down at 3 AM, should it retry or just tell you in the morning?" Their answers become the procedure's failure and no-result sections.

## 4. Pick the trigger

Choose the trigger type based on where the signal comes from, not on how the user phrased the request:

- **Time itself is the signal** — the automation should run on a schedule. Use `--cron` for recurring or `--start` for a one-shot.
- **The source pushes a signed event** — use a webhook trigger. The source notifies Helio when something happens.
- **The source has no reliable push mechanism** — use a poll trigger. A lightweight check runs on a cron schedule and fires the automation only when it finds something worth acting on.

"Checking every five minutes works fine" is a statement about acceptable delay, not a reason to poll instead of using a webhook. If the source supports webhooks, prefer them — they are fresher and avoid wasted checks.

Pass the source's stable delivery id as `fire_key` — it is the idempotency boundary that prevents duplicate runs on retries.

For the full handler contract, signature verification, packaging, fixtures, deployment, and logging details, read [`references/event-triggers.md`](references/event-triggers.md).

## 5. Create it

Build the argument array as JSON and pass it through the args-file transport:

```json
["automation", "create", "<name>", "--cron", "0 9 * * 1-5", "--owner", "@<requester>",
 "--procedure", "# <name>\n\n## Objective\n<approved objective>\n\n## Procedure\n<approved steps>"]
```

```bash
heliox --json --args-file /absolute/path/create-automation.json
```

Use either `--cron` or `--start` (one-shot), not both. When converting the user's phrasing to a cron expression: an explicit clock time is an exact cron ("every day at 9 AM" = `0 9 * * *`); vague wording ("every morning") gets a randomized minute offset so that all loosely-timed automations do not fire at the same second.

`--procedure` takes the markdown BODY, never a filename — the AI that executes this procedure days or weeks later cannot read a file path that existed on your runtime at creation time. Draft in a local file if it helps, but paste its contents into the argument JSON; the file serves only as `--args-file` transport.

The procedure write is a second request after create. After creating the automation, verify the procedure landed correctly: `heliox document read <document_id>` should show the approved procedure text, not an empty body or a file path. If it does not match, fix it before moving on — do not hand over an automation whose procedure is blank or wrong.

Every automation is created disabled. Enabling it is the user's decision, not yours — they may want to validate it first, or they may want to enable it immediately. Either way, the choice is theirs.

## 6. Hand it over

Tell the user what now exists and what is still unproven:

- The automation id and its name
- How it triggers (schedule, webhook, or poll) and the cadence or event
- Where results go and who receives them
- Which paths from step 3 have not been exercised yet

The next step — validating the automation with real or simulated runs, tuning the procedure, enabling it, and maintaining it over time — belongs to `heliox:automation-refiner`. Point the user there if they want to go further.

Enabling is the user's call. If they say "turn it on," go ahead. If they do not, leave it disabled and tell them how to enable it when they are ready.

## The procedure document

Self-contained markdown from the approved execution, using the sections that apply:

```markdown
# <name>
## Objective
## Inputs and freshness
## Procedure
## Output and delivery
## Failure and no-result behavior
## Done when
```

For recurring scans, digests, or watches, `## Inputs and freshness` pins the read scope: the exact sources to check, the filters to apply, and a time window derived from the cadence. A daily scan reads the last day's data, not everything ever written. A weekly digest covers the last week. The window matches the cadence so that each run sees exactly its own period and nothing from the previous one.

A bounded read that finds nothing within that window is the no-result path — it means this period was quiet. The procedure should describe what to report in that case (see step 3). It should not page past the window or drop filters to manufacture a non-empty result.

Keep evaluation cases, grades, and execution ids out of the procedure. The procedure is what the executor reads to do the work; test artifacts belong alongside the automation, not inside its instructions.

## Output language

- Name, description, and procedure follow the user's own instruction language — not a wrapper sentence around it. A mixed-language instruction follows its dominant language.
- If the instruction is too short to tell (a one-line edit), fall back to the language the conversation is in.
- This applies to artifacts only — conversational replies stay in the conversation's language, so the two can differ.

## Boundaries

A procedure is a maintained document, not a program. It describes what to do in prose that an AI executor reads and follows. If you find yourself writing conditional logic, loops, or branching control flow inside the procedure, you are building something that should be code, not a procedure.

One automation is one coherent job. If the user asks for two different things on two different schedules, those are two automations, not one automation with internal branching.

---

Keep these six steps in your working list so you do not skip step 3 (the unseen paths) or the procedure readback in step 5:

1. Pin down what they want
2. Do the work once, here
3. Write down the paths you did not see
4. Pick the trigger
5. Create it
6. Hand it over
