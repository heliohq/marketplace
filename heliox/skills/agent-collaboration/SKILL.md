---
name: agent-collaboration
description: "Use first in any Helio group channel where multiple AI agents share a task, roles like lead/reviewer/writer/specialist are present, or one shared report, patch, artifact, or final answer must be produced. Use even when the prompt is pure work and does not explicitly mention collaboration. Do not use for ordinary 1:1 DMs or single-agent tasks."
user-invocable: false
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox message --help"
---

# Agent Collaboration

Use this skill when the channel is a real team: more than one AI teammate is
present for the same task, or the user has asked agents to work together. In a
DM or single-agent channel, keep using normal judgment.

Collaboration means complementary progress, not parallel solo answers. The goal
is to make ownership visible, prevent duplicate artifact work, and still give
the current owner useful handoffs, review notes, and evidence.

This skill comes before domain execution. In a group channel with one shared
output, do not open a research, writing, coding, or other specialist workflow
until role and artifact ownership are clear. Once ownership is clear, the lead
or current owner can use specialist skills and tools without bypassing the team.

For `heliox message ...`, keep normal safe-message habits: read recent messages,
send with the latest seen sequence, re-read before posting into a busy group,
avoid shell-splicing generated prose, and cede when a teammate already covered
your useful point.

## First Move

Read recent channel history before substantive work. Decide whether someone has
already claimed lead, writer, reviewer, specialist, or observer.

Use your preset role as your default claim:

- Lead or coordinator: coordinate the team.
- Writer or implementer: own the artifact only when the lead hands it to you or
  no better lead is present.
- Researcher or specialist: provide a narrow evidence lane or handoff packet.
- Reviewer or critic: stay read-only unless reassigned before work starts.

Before substantive work, make your current role visible unless you are ceding.
The role claim is the work acknowledgement. Do not send a separate generic
promise before the room knows who is leading, who is writing, and who is
reviewing.

Do not make the role claim your whole contribution. If you have enough context
to help, claim or confirm your lane in a sentence and then move that lane
forward in the same turn with evidence, a plan, review notes, or the next
handoff. Pause only when you truly need the lead or another teammate to assign
ownership first.

If a natural lead is present, give them the first coordination move. If you wake
before them, briefly offer your lane or stay read-only; do not claim the whole
task just because you saw the prompt first.

If no lead is clear and the task needs coordination, either claim lead when it
fits your role or invite the best-fit teammate already in the channel to take
lead.

## Lead

A team needs one current lead. If you are lead:

- Break the task into visible pieces.
- Use the agents already in the channel as the team before creating private
  parallel work.
- Name one current owner for any artifact, patch, report, or final answer.
- Ask reviewers and specialists for specific checks instead of letting everyone
  produce a parallel version.
- Re-read recent messages before launching broad work. If a teammate already
  started the same lane, use their output as raw material or ask for a handoff
  instead of duplicating it.
- Resolve blockers and decide what gets accepted.
- Send the final synthesized result or closeout yourself.

Your first lead message should create the working shape, not just promise
progress. Name the lead, the artifact owner, the first review or specialist
lanes, and the next handoff. Then keep moving; do not let the kickoff become
the whole turn.

## Artifact Ownership

Only one agent writes the artifact, document, patch, report, or final answer at
a time. Everyone else is read-only unless the lead explicitly hands them the
writing role before work starts.

Drafts, diffs, notes, and candidate answers from non-owners are review material,
not the team's final output. If more than one agent starts the same artifact,
pause and let the lead reset ownership.

Read-only does not mean idle. Non-owners can provide compact material the owner
can use directly: evidence bullets, requirement coverage, edge cases, blockers,
and approval notes. Label these as handoff material rather than final output.

A target file, patch location, report path, or final-answer instruction in the
human prompt is the team's destination. It does not override your role. Do not
write, overwrite, or finalize that destination unless you are the current owner.

## Review

Reviewers and critics improve the work; they do not submit it. Give comments,
blockers, missing evidence, risk calls, and approval notes. Do not rewrite the
artifact or send the final answer unless the lead reassigns you as writer or
lead first.

If no draft exists yet, ask for a concrete review target or provide a short
acceptance checklist. Do not create the artifact just to have something to
review.

## Final Delivery

If the task asks for one shared artifact, one final answer, or a standalone
completion marker, treat that as team-level delivery. Only the current lead or
explicitly assigned writer sends it after the artifact or final answer exists
and review blockers are handled.

In ordinary channel collaboration, do not talk about markers. Send the final
answer in the normal human shape.

## Examples

Lead claim: "I'll lead this. Sam, please check sources; Priya, review the final
answer for risk. I'll own the synthesis and close it out."

Reviewer claim plus work: "I'll review, not write. Current gaps to watch:
source support for X, a decision on Y, and whether Z is in scope."
