# Conversation Templates

## First reply (FIRST_REPLY state)

```
**Created (disabled):** Daily GitHub email digest — every day 9:00 (Australia/Melbourne), summarizes the last 24h of GitHub emails into a table, delivered to this DM.

Assumptions I made (reply to correct any):
- GitHub senders only, not mails that merely mention GitHub
- Summaries in Chinese
- Delivery: this DM

Your checklist (3 items — after these I rehearse automatically):
1. Connect Gmail: <authorize link> — this automation reads your GitHub emails there.
2. Install lark-cli on this machine — rehearsal needs it to format the output table. See the Lark developer docs for installation.
3. Your Lark login email — so the bot can send you the report as a P2P message (the recording only shows the display name "Yang", which is not an address).

Complete these 3 items and I will rehearse automatically and post the result here. Nothing runs on a schedule until you approve.
```

The numbered checklist contains every action the user must take — connect links, binary installs, user-only facts, and fork decisions — in dependency order, each on one line. Items the assistant can default are assumptions (un-numbered bullets), never checklist items. If PREFLIGHT found nothing for the user to do, the checklist block is omitted entirely, the closing line becomes: "I am rehearsing it now and will post the result here. Nothing runs on a schedule until you approve." — and the rehearsal starts in the same turn (no connection is pending, so no wake will arrive).

## ALTERNATIVES template (step not coverable by current capabilities)

```
**Not realizable as recorded:** [which part of the recording, and why — missing provider/skill].

**What I can do instead (pick one, or say no):**
1. [alternative route using an available/connectable capability] — [what changes vs the recording]
2. ...
```

Never apply a substitution the user has not picked.

## HALT template (no viable alternative found, or all rejected)

```
I cannot build this automation because [specific reason].

The closest options I found and why they fall short:
- [ruled-out route] — [why it falls short]
```

Do not soften the HALT. Do not create a partial automation.
