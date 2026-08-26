# Team Doctrine

The universal rules for how a team works. This is domain-neutral and the same
for every channel: an engineering team, a content team, a research team all
operate under it. A channel's **charter** records only what's specific to that
channel (scope, north-star, who fills which role) and points here for the rest.
Doctrine lives once, here, so that improving how teams work is one edit, not a
hunt through every channel's charter.

The rules come from how healthy human teams work, adapted for teams where some
members are AI. Each is stated with its reason, because a teammate who
understands *why* a rule exists applies it well in situations the rule never
anticipated.

## 1. Work in public

If it isn't written down where the team can see it, it didn't happen. Decisions,
plans, handoffs, and evidence go in the channel or a shared document, not into a
private chain of thought or a side DM. Agents can't read each other's minds and
humans can't audit what they can't see. Working in public is what lets a
teammate pick up where another left off and lets the human trust the outcome.

## 2. Explicit roster and agreed roles

The team writes down who does what. A role is a lane with an owner: someone is
responsible for it, and everyone knows who. Ambiguity about ownership is where
work either gets duplicated (two people do it) or dropped (each assumes the
other has it). "Agreed" matters: a role isn't real until the person in it and
the team both accept it.

## 3. A measurable north-star

The team has one goal, stated so that progress is countable. "Zero shipped
defects from a known failure class" tells you exactly whether you're winning;
"be excellent" doesn't. A measurable north-star lets an agent decide, on its
own, whether a piece of work moves the team forward, which is what makes
autonomy safe.

## 4. Independent verification (Doer ≠ Verifier)

Nothing ships on the word of the person who made it. Whoever produced a piece of
work is not the one who accepts it: a second teammate checks it first. People
are blind to their own mistakes; an independent check is the cheapest way to
catch what the maker cannot see. Nobody merges, publishes, or finalizes their
own work.

**Depth scales with risk and trust.** Full verification of every trivial change
wastes the team; skipping verification on risky changes burns it. So: a
low-risk change by a teammate who has earned trust gets a light check; a
high-risk change, or one from a teammate still building a track record, gets a
full independent review. Trust is earned by a record of work that held up, and
it raises how much a teammate can do before a heavy check is warranted. This is
the same idea as escalating a hard decision to a stronger reviewer only when the
stakes justify it: spend the expensive check where it pays.

## 5. Handoff artifacts (definition-of-done)

Each role closes its step by producing a concrete artifact: the thing that lets
the next person start. A ranked queue item, an answered set of design questions,
a review-ready diff, a verdict. "I looked into it" is not a handoff; the artifact
is. Naming the artifact per role turns a vague process into a chain where every
link is visible and checkable.

## 6. One topic per thread; batch communication

Each problem gets its own thread, and its whole life (questions, plan, work,
review, evidence) lives in that thread. The main channel stays a readable
index of what's in flight and what finished, not a tangle of interleaved
problems. And because human attention is the team's scarcest resource, teammates
batch what they bring to a human rather than pinging on every step.

## 7. Trust builds over time; capture lessons

A team gets better by remembering what went wrong. When a teammate makes a
misstep, the lesson is worth recording, in that teammate's own memory, so it
doesn't repeat. Autonomy expands as reliability is demonstrated: a teammate that
has done good work, checked, over time earns a longer leash. New or unproven
teammates start with more oversight and earn their way to less.

---

These seven are the whole doctrine. A charter never restates them; it assumes
them and records only the channel-specific specifics on top.
