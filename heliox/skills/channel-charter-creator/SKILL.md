---
name: channel-charter-creator
description: "Use FIRST in an organic group channel where more than one teammate (AI or human) shares a goal and the runtime prompt does not already contain a managed team operating context. It establishes how the team coordinates: if the channel already has a team charter, it points you to your role and how to operate under it; if there is none, it runs a short formation ritual (learn the roster, agree roles, a measurable north-star, and independent verification) and records a charter the whole team operates under. A managed hired-team context is already the channel's hidden operating agreement: follow it silently and do not run this ritual. Do not use in 1:1 DMs or single-agent channels."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox channel --help"
---

# Channel Charter Creator

A group channel with more than one teammate is a **team**. Teams coordinate
well when they share one agreement about who does what, what "done" looks like,
and how work gets checked: a **charter**. Teams without one drift: two agents
write the same artifact, nothing gets verified, the human gets pinged for
decisions they never agreed to own. This skill's job is to make sure the team
has a good charter and that you operate under it. In a DM or single-agent
channel, none of this applies. Use normal judgment.

If the runtime prompt contains **Managed team operating context**, stop here:
that hidden channel contract already binds the coordinator, specialists,
handoffs, and user-override rule. Follow it silently. Do not create a charter
document, change the channel description, announce a formation ritual, or ask
the user to ratify the arrangement. A current explicit human instruction may
override its collaboration defaults exactly as the context says; safety,
permissions, and approval requirements remain higher priority.

The charter is a shared, durable **team agreement**, not moment-to-moment
chatter. It lives once, channel-scoped, as a collaborative document, and it is
the single source of truth. You read it; you do not keep a private copy (a copy
is a fork that drifts).

## First move: is there a charter?

Before any substantive work, find out whether this channel already has one.

```bash
heliox channel show '#<channel-name>' --json   # .channel.description carries the charter pointer
```

A charter pointer in the channel description is either
`📋 Team charter: https://app.helio.im/document/<id>` or the legacy
`📋 Team charter: helio://document/<id>`. Treat both as present; only the public
HTTPS form is written for new or replaced pointers. The pointer is published
only after the human owner ratifies (**a description pointer means a ratified
charter**), so operate under it without re-checking its status.

- **Pointer present** → go to **Operate under the charter**. This is the common
  path and it is light: a read, not a re-authoring.
- **No pointer** → don't rush to create; check for a ritual or a charter you
  can't see from the description. Skim recent history
  (`heliox message list '#<channel-name>' --limit 50`):
  - A formation ritual is already underway: a draft announced, awaiting
    ratification → **join that thread**. Never start a second ritual.
  - The history or a teammate references an existing charter document → reuse
    that document; never create a duplicate when there is evidence one exists.
    (Cross-document search is not implemented; the pointer and the channel's
    own record are the discovery surface.)
- **Nothing found, and this is a real team** (≥2 teammates on shared work) → go
  to **Run the formation ritual**. Offer it; don't silently impose it.

## Operate under the charter

Read the charter document, then act. Do not stop at reading.

```bash
heliox document read <document-routeUrl>
```

From it, find four things and hold them for the rest of your work in this
channel:

1. **Your role** and what you own (your lane). Stay in it unless reassigned.
2. **Your handoff artifact**: the deliverable that lets you close your step
   (a ranked item, an answered design question, a PR-ready diff, a verdict). A
   step isn't done until its artifact exists.
3. **The verification rule**: nothing ships without an independent check by
   someone other than its author (Doer ≠ Verifier). Depth scales with risk and
   trust (see doctrine): a low-risk change by a trusted teammate gets a light
   check; a risky or unfamiliar one gets a full check.
4. **The working rules**: one topic per thread, decisions written down, work
   in public.

Also hold the **north-star**. It isn't only what your work is judged against.
If your role lets you propose work, it's your license to *proactively* surface
things that move the team toward it, rather than only executing what you're
handed. If your role is execute-only, stay in your lane and route ideas to
whoever may propose.

Once per arrival (when you begin working in this channel, not on every
message), check the roster hasn't drifted: compare the charter's Roster & roles
against live membership (`heliox channel members list '#<channel-name>'
--json`). If a member is present but unassigned in the charter, or the charter
binds someone who has left, flag it in the channel or thread and propose a
re-bind through **Amendments**. Do not silently operate on stale bindings for
the affected members; the rest of the charter still applies.

If a piece of work forces a product decision the charter didn't settle (scope,
priority, a hard trade-off), stop and ask the human who owns that call. Do not
decide product inside execution.

The full team doctrine these rules come from is in `references/doctrine.md`.
Read it once if you need the reasoning; the charter itself only records what is
specific to this channel and points at the doctrine for the rest.

## Run the formation ritual

Producing a *good* charter is the point. A bad one is worse than none because
the team trusts it. Work through these steps; the quality bar at the end is what
"good" means, and you should not record a charter that fails it.

### Step 1: Know the roster (do this first; it is load-bearing)

You cannot assign roles to people you don't know. Learn the team:

```bash
heliox channel members list '#<channel-name>' --json    # who is here: resolved user (@handle), type (human|ai), permission role
heliox workspace members list --json                    # the whole org roster: handle, name, type, bio
heliox assistant show @<handle> --json                  # one AI in depth: bio, model, channels
heliox message list '#<channel-name>' --limit 50       # what they've actually done
```

Each `channel members list` row carries one resolved `user` field (`@handle`,
falling back to display name, then bare id), a `type` field (`human` | `ai`)
that answers the AI-ness question directly, plus `role` and
`notification_level`. Bios live on the `workspace members list` row for the
same person. A row whose `type` is absent (and whose `user` renders as a bare
24-hex) means the workspace cache could not resolve that member yet. Re-run
the command rather than guessing.

Note the trap: the `members list` role is a **permission** (`admin`/`member`),
**not** a work-role. A teammate's actual responsibility, if written anywhere,
is in their freeform `bio` (which may be empty), and humans have no
responsibility field at all. So a work-role is something you **propose from bio
plus behavior**, never read as a fact.

Therefore: read what's declared, then **ask for what isn't.** Where a bio is
silent or ambiguous, @-mention the member and ask, plainly, "what's your role
here, and what do you own?" Let them self-declare. For humans, let the human
state their own role. If several members are unclear, ask them in **one batched
message**, not a separate ping each. Never silently guess a role onto someone; a
member with no derivable role is a question to ask, not a blank to fill.

### Step 2: Get the product calls from the human

Some things are the human's to decide, not yours (surface them, don't invent).
Ask them in **one batched message**, not one at a time. Human attention is the
team's scarcest resource, and drip-questioning burns it:

- **Scope**: what this channel owns, bounded. "This channel, not everything."
- **North-star**: the team's goal, stated so success or failure is
  *countable*, not a vibe. "Zero shipped bugs from a known drift class" is
  measurable; "high quality" is not. (It doubles as each teammate's proactive
  license; see *Operate under the charter*.)
- **Who may proactively propose work** toward the north-star. The human names
  which teammates can suggest new workstreams on their own vs. only execute what
  they're handed. Without this, agents either sit idle or over-reach.

If the human isn't available, draft the charter with these marked as open and
wait to finalize. The team can operate on defaults meanwhile, but the human
ratifies before it's real.

### Step 3: Compose the charter

Fill the six-section shape in `references/charter-template.md`. It is
domain-neutral on purpose: the same shape serves an engineering team, a content
team, a research team; only the vocabulary changes. Draw role names and their
default handoff artifacts from the members' own profiles and the team's domain,
not from a fixed engineering vocabulary.

Reference the doctrine in plain text; do not restate it, and do not put local
markdown links to this skill's reference files in the charter body. The charter
records only what's specific to this channel (scope, north-star, roster→role,
artifacts). The universal rules (work in public, verification, thread
discipline) live once in the doctrine and the charter names them. Restating
doctrine per channel is how it drifts.

### Step 4: Check it against the quality bar

Do not record a charter that fails the **quality bar in
`references/charter-template.md`**. That checklist (six sections present; every
member has a role; every role has an artifact; an independent verifier exists;
the north-star is countable; scope is bounded) is what protects a human who
doesn't know charter-craft from getting a bad one. It lives once, next to the
template shape it validates.

If something fails, it's usually because Step 1 or 2 is incomplete. Go back and
ask, don't paper over it.

### Step 5: Record the draft; publish only after ratification

The charter is generated prose with characters the shell will mangle. Never
splice it into a command line. Write the argv as JSON and run
`heliox --args-file <path>`, which passes the text as data.

**Record the draft.** One call creates the channel-bound document and seeds the
full body. Mark the header line `DRAFT - awaiting ratification` per
`references/charter-template.md`. The header is where draft status lives:

```bash
# create_doc.json (written with your file tool):
#   ["document","create","Team Charter - #<channel-name>",
#    "--channel","#<channel-name>",
#    "--content","<full charter markdown, header marked DRAFT>",
#    "--json"]
heliox --args-file create_doc.json
```

`--content` seeds the body at create time; do not create empty and try to
edit: `document edit` cannot write a first body. If the seed fails, the error
reports the created document id: do **not** create a second charter document.
Fix the cause (usually a dead `helio://` link in the body; a charter body needs
none) and retry the body write with `heliox document seed <id>` (same
`--content`, through `--args-file`), which fills an empty document and refuses
a non-empty one.

**Announce and hand off.** Post in the channel: the scope, north-star, and
roster→role in brief, the document link, and an explicit ask for the human
owner to ratify or adjust. It is a **draft until the human ratifies**: you
surface the product calls, they own them. Do not publish the description
pointer yet: teammates treat a pointer as a ratified charter (see First move).

**After the human ratifies, only then:**

1. Flip the document header from `DRAFT - awaiting ratification` to `v0.1`
   with `heliox document edit` (through `--args-file`; the header carries `#`).
2. Publish the pointer into the channel description, by **merge**, never
   replace: `channel update --description` overwrites the whole description,
   so writing only the pointer would erase human-written description text.
   Read the current value (`heliox channel show '#<channel-name>' --json`; the
   response wraps the channel, so the field is `.channel.description`); if a
   `📋 Team charter:` line already exists,
   replace that line, otherwise append `📋 Team charter: <document routeUrl>`
   on its own line; write the merged text back (arbitrary prose →
   `--args-file`):

```bash
# update_desc.json (written with your file tool):
#   ["channel","update","#<channel-name>","--description","<merged description>","--json"]
heliox --args-file update_desc.json
```

## Amendments

Charters change as the team learns. Propose an amendment in-thread. Roster
drift found by the arrival check lands here too. The human owner ratifies; then
edit the document in place
(`heliox document edit <document-routeUrl> --old ... --new ...`, through
`--args-file` when the text is prose) and bump the version line. Editing the
one document keeps it the single source of truth. Do not fork a new copy or
paste the charter into a message.

## What goes where

Shared team agreement → the shared document. What's *yours* (the lessons,
missteps, role notes, and trust you accumulate operating under it) → your own
`heliox memory`. Don't put private notes in the charter, and don't copy the
charter into your memory (a copy is a fork that drifts).
