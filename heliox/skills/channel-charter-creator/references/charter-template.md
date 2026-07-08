# Charter Template

The shape every charter takes. It is deliberately domain-neutral — the same six
sections serve any team; only the words inside change. Fill each section for the
specific channel. Keep it thin: this records what's specific to *this* channel
and names the Team Doctrine in plain text for the universal rules. If you find
yourself restating the doctrine, stop; do not insert local markdown links such as
`doctrine.md` or `references/doctrine.md` into the charter body.

## The six sections

```markdown
# 📋 Charter — #<channel-name> · <DRAFT — awaiting ratification | vX.Y>
> Operates under Team Doctrine: work in public, independent verification,
> measurable north-star, thread discipline). This charter records only what's
> specific to this channel. If the two disagree, the doctrine wins.

## Scope
<What this channel owns — bounded. State what it does NOT own and where that
work goes instead, so nobody land-grabs across boundaries.>

## North-star
<The team's goal, stated as a countable success/failure class. Include the
metric and the target, e.g. "Metric = X; target = 0." Also name who may
*proactively* propose work toward it (vs. execute-only roles) — the north-star is
what makes that proactivity safe.>

## Roster & roles
<Every member (human + AI) → at least one role. No member unassigned; no
critical role unfilled. For each: member, role, and one line on what they own.>

## Handoff artifacts
<For each role, the concrete deliverable that closes its step — its
definition-of-done. This is what makes the chain checkable.>

## Verification
<Who checks what before it ships. Doer ≠ Verifier. State how depth scales with
risk/trust for this team — what gets a light check vs. a full one.>

## Working rules
<Only the channel-specific rules on top of the doctrine. One topic per thread,
where decisions are recorded, anything specific to this team's medium.>

## <version + amendment line>
<The header status is the lifecycle: seeded as "DRAFT — awaiting ratification";
when the human owner ratifies, flip it to "v0.1"; amendments bump it. e.g.
"v0.1 · ratified by <human owner> · amendments proposed in-thread, <human
owner> ratifies, document updated.">
```

## Quality bar (do not record a charter that fails this)

- [ ] All six sections present.
- [ ] Every member mapped to ≥1 role; none unassigned, no critical role unfilled.
- [ ] Every role has a named handoff artifact.
- [ ] An independent verifier exists for anything that ships (Doer ≠ Verifier).
- [ ] North-star is measurable (has a metric and a target).
- [ ] Scope is bounded (says what's out, not just what's in).

## Two fillings, to show the shape is general

Both are generic, made-up teams — the machinery is identical and only the
vocabulary changes. Do not copy either of these; derive the roles and artifacts
from the actual members and the team's real domain.

### A software team

- **Scope:** the backend of one service the team owns; not the client app
  (another team owns that), not shared infrastructure.
- **North-star:** no user-facing defect ships from a failure class the team has
  already fixed once. Metric = repeat-class defects shipped; target = 0.
- **Roster & roles:** one member *Doer* (implements + owns the change) · one
  *Verifier* (reviews; never ships own work) · one *Intake* (watches error logs
  → ranked queue) · a human *Product-owner* (scope + priority calls).
- **Handoff artifacts:** Intake → ranked item (symptom + area + hypothesis);
  Doer → change with tests + evidence; Verifier → verdict + caveats.
- **Verification:** a trivial change by a trusted Doer → one light pass; any
  change to stored data or an external contract → full review before ship.
  Doer ≠ Verifier.

### A content team

- **Scope:** launch-announcement posts for the product's releases; not the docs
  site (another team owns that), not social distribution.
- **North-star:** every published post traces to a real release and passes
  fact-check. Metric = posts published with an unverified claim; target = 0.
- **Roster & roles:** one member *Writer* (owns the draft) · one *Fact-checker*
  (verifies claims; never publishes own draft) · one *Intake* (watches releases
  → topic briefs) · a human *Editor* (voice + go/no-go).
- **Handoff artifacts:** Intake → topic brief (release + angle + audience);
  Writer → draft with every claim source-linked; Fact-checker → claim-by-claim
  verdict.
- **Verification:** a wording pass is light; any factual or feature claim gets
  an independent source-check before publish. Writer ≠ Fact-checker.

Notice the sections, the artifact-per-role discipline, and Doer ≠ Verifier are
the same in both. That sameness is the point — the doctrine holds; the domain
just fills it in.
