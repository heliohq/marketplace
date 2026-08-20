---
name: user-wiki
description: "Own the user wiki, the living document about your owner: who they are, how they write, who they work with, what they have in flight. Use this skill every time the wiki is touched. An onboarding kickoff directive names it (first build); the owner connects a new tool (refresh); the owner says anything like 'my wiki', 'update my profile', 'redo what you know about me'; or you learned something about your owner that belongs on the page. The wiki is the owner's heliox document, visible and editable by them and updated in place. It is never your private brain wiki."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox document --help"
---

# User Wiki

The user wiki is one collaborative document about your owner. It is theirs:
they see it, they can edit it, and it gets more accurate the longer you work
together. Your job is to keep it true.

One wiki, one document id, always. Never create a second wiki document.

## Which mode you are in

The wiki's pointer lives at a fixed path, `brain/wiki/user-wiki.md`, holding
the document id and routeUrl. The first build writes it. One command decides
the mode: `cat brain/wiki/user-wiki.md`.

- **File missing or empty: first build.** Read
  [references/first-build.md](references/first-build.md) and follow it
  exactly. It is a timed, watched run with its own command budget.
- **File has a document id: refresh.** Continue below.

## Refresh

A refresh happens when the owner connected a new tool, asked you to update the
wiki, or you learned something about them worth recording.

1. `heliox document read <id> --json` gives you the current page, including
   any edits the owner made themselves. Their edits are facts about what they
   want on this page: reconcile with them, never overwrite them wholesale.
2. If a new tool was connected, read it as described below before you write
   anything.
3. Apply surgical `heliox document edit` replacements. `--old` is exact
   contiguous text copied from the `document read` output, which is rendered
   plain text, so markdown markers like `##` never appear in it and never
   match. `--new` is the corrected passage. Batch independent edits in one
   exec.
4. Update your brain wiki notes if what you learned changes them.
5. Answer the way you were invoked. A system wake tells you in its envelope
   which surfaces to deliver on; an owner asking in chat gets a normal short
   reply with the document link. Push a desk suggestion only for evidence
   this scan turned up that is not already a row on their desk, so read
   `heliox feed list` before you push.

## Rules that hold in every mode

- **Write only what you read; never promote a guess to a fact.** Unsure means
  hedge ("looks like…") or leave it out. One wrong personal fact costs more
  trust than ten right ones earn.
- **Sensitive content never enters the wiki.** Salary, medical, credentials,
  anything your owner would not want to see written on this page, stays off
  it even when a scan surfaces it. Wedding planning yes, lab results no.
- **Every section has a body.** Where evidence is thin, write one honest line
  in your owner's language saying you have not read enough about this yet and
  will add it as you work together. Never leave a placeholder line standing,
  never delete a section, and never add a second snapshot footer. The page
  already ends with one.
- **The whole page is in your owner's language** — title, headings, bodies,
  and footer alike. [references/page-template.md](references/page-template.md)
  fixes the sections and their order; you write their headings in your
  owner's language yourself. Never mix languages: an English heading over a
  Chinese body is wrong.
- **Ideas the owner dismissed stay dismissed.** Desk rows they rejected do not
  come back reworded. Stale rows you authored get `update` or `withdraw`, not
  a duplicate.

## What to read (any mode that reads tools)

**Read what your owner made, not what arrived for them.**

Most of what a connected tool holds, your owner never wrote. Other people and
mailing lists fill their inbox. Their calendar carries invitations they never
opened. Their Slack has channels somebody added them to and they never posted
in. Ask any of those tools for the newest fifty items and almost all fifty
will be things that arrived, which tells you who was contacting them and
nothing about them.

The part they wrote themselves is much smaller and it is the only part that is
actually about them. It also hands you a second fact for free: whoever is on
the other side of something they wrote is somebody they really deal with.
Neither fact needs any filtering, which is why this still works in tools where
a filter would not.

So ask every connected tool the same question, listed here or not: what in
here did my owner make? Then read the one step outward named in the table
below, which is how you pick up the other side of an exchange they joined.

| Tool | What they made | One step out |
|---|---|---|
| Email | Messages they sent | The whole thread each one sits in |
| Calendar | Events they created or accepted | Who recurs across them |
| Slack / Lark / chat | Messages they posted | The channels they posted in |
| Docs / Notion / Drive | Pages they created or last edited | Who else edits those |
| Issues / code hosts | Issues, PRs, comments they opened | The threads under them |

A tool where they made nothing cannot tell you who they are. Put its name in
the tools list and move on. Reading it anyway is how a page fills up with
other people's words.

**Wide, then deep.** The wide pass lists headers only, as many as the tool
returns in one call, and tells you who and how much: every name on the other
side, every title. Then rank what the wide pass returned by how much of your
owner is in it, meaning the people who recur most, the exchanges that ran
longest, and the ones they wrote most in. The deep pass opens the top 15 to
25 of that ranking in full, and tells you how they write and what they are in
the middle of. Each pass is one exec. Go deep first and you will read twenty
items at random before you know which twenty mattered. Quote and mark only
what a pass actually opened: list snippets truncate mid-sentence, and a mark
on an unread item is a claim you cannot back.

**Nothing you or Helio produced is evidence.** Your own briefings,
notifications, and test messages sit in the same places, addressed to your
owner, so they look like signal. Quote one back and the page records
something you said.

Learn a tool's commands from its guide file rather than by probing:
`<skill-dir>/../tool/<name>/<name>.md`, or for grouped providers
`<skill-dir>/../tool/google/gmail.md`, where `<skill-dir>` is the directory
this SKILL.md loaded from. The guide is also where each tool spells "mine":
Gmail takes a search query, Notion has `created_by` and `last_edited_by`,
calendars separate the organizer from the attendees. A tool with no guide file
gets a single `heliox tool <name> -- --help`. Fire every read of a pass
concurrently in one exec. A source that errors gets one line in the wiki's
footer area and no retries. Reading deeper than this belongs to real tasks
rather than wiki passes.

## Page format

Your owner skims this page in ten seconds. Every line should be something they
can nod at ("yes, that's me") or correct on the spot, which is what the page
is for.

- **Bullets, not paragraphs.** Each section body is a `- ` list of 2 to 4
  items, and Personal context may be 1. Each item states one checkable fact
  and fits on one line. Connected tools and the honest thin-evidence line stay
  plain single lines.
- **Open every line with what your owner does.** The title already names
  them, so a line never repeats their name, never addresses them as "you",
  and never starts with the tool the fact came from. In English use the plain
  present tense ("Runs", "Advises", "Blocks"), not "Is running", which reads
  as a sentence with its subject knocked off. Same evidence, written both
  ways:

  | Not this | This |
  |---|---|
  | `Gmail sent messages use the name "Nadia Okafor"` | `Runs a two-person bookkeeping practice out of nadia@ledgerroom.co` |
  | `Calendar is labeled "Mira Persson" and uses Europe/Stockholm` | `Works Stockholm hours and keeps Fridays clear of meetings` |
  | `Is preparing the October board deck for Thursday` | `Prepares the October board deck for Thursday` |

  Key contacts is the exception: there the other person IS the subject, so
  those lines open with their name, as in
  `- Kwame Boateng: the supplier they chase about lead times ¹`. Four lines
  that all open "Works with…" bury the one word the reader is scanning for.
- **Source marks.** Number your real sources ¹ ² ³ (unicode
  superscripts), one per anchor you actually cite. A mark resolves to exactly
  one thing: one provider and one item your owner would recognize. Never join
  two providers or two channels under one number, because the whole use of a
  mark is that a line your owner disagrees with points at the one place to go
  look. Six marks is about as many as a page can carry; if you want more, you
  are citing single items where a thread or a channel would do. An item that
  came from a source ends with its mark or marks,
  e.g. `- Signs off "Warmly, Travis" to people outside the team ¹`. The
  Sources section lists each numbered source on its own line, like
  `¹ Gmail·"October application tracker"` or `² Slack·#essay-team`: one
  concrete anchor the owner will recognize, such as a thread subject, a
  channel, or an event title. "Your email" is not an anchor. The honest
  thin-evidence line carries no mark.

## What the page covers

[references/page-template.md](references/page-template.md) fixes the sections
and their order; this table fixes what goes in each. The names below are the
template's English reference names — the live page carries them in your
owner's language, so when a refresh needs a heading exactly as it must be
typed, copy it from the `document read` output, never from here.

| Section | Write | Evidence |
|---|---|---|
| Identity | What they do, where, and from which address, plus the name they actually go by, when that differs from the name in the page title. Their own name is not content here: the title carries it, and repeating it is what pushes the person out of their own sentence. A hedged reading of good evidence beats an omission ("appears to advise on US applications, since a colleague addresses them as a teacher"); an unhedged guess is worse than both. | Their signatures, their domains, how people address them. |
| Key contacts | 2 to 4 named people they exchange messages with. Open each line with the person's name, then what your owner deals with them about. A company, a mailing list, or a name that merely appeared in a subject line is not a contact. If nobody qualifies, say so instead of filling the section. | Who is on the other side of what they sent. |
| Communication style | Language habits (when they use which language), tone, structure, and sign-offs. Quote the actual sign-off strings, per language. | What they wrote. |
| Work patterns | Their rhythm and what they have in flight. Name the concrete projects and deadlines. | What they wrote, their calendar. |
| Working preferences | 1 to 3 rules you could act on tomorrow, each from something they did more than once ("returns edited files as Word and PDF", "confirms with the student before a second revision"). This is the only section that changes what you do; the rest only describe them. | Repeated behavior in what they wrote. |
| Personal context | Things they plan or care about outside work, limited to what they would happily see written here. | What they wrote, their calendar. |
| Writing samples | 2 to 3 verbatim excerpts they typed themselves, each labeled with the situation. Cover different situations rather than three of the same: how they open with an outsider, how they ask for something with several parts, how they update a colleague in passing. Skip anything auto-generated, boilerplate, or one word long. If nothing they wrote is worth quoting, say so. | What they wrote. |
| Connected tools | One line: which tools are connected, and which were unreadable this pass. | Tool list plus scan outcome. |
| Sources | The numbered source lines the marks resolve to (see Page format). | The scan itself. |

The page ends with the template's snapshot footer. Keep it, and never add a
second one.
