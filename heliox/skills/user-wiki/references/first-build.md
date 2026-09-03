# First build, the onboarding pass

Your owner just connected their tools and is watching you work, live. Come
back with two things, in this order:

1. **Their wiki**, filled from their own data.
2. **Their first tasks**: 5 to 9 non-duplicate desk suggestions when the
   evidence supports that many (aim for 7, never pad), each one they could
   accept on the spot and each pointing at something concrete you read.

Your owner waits through every command, so the whole pass fits in **ten
commands or fewer**. Command count is the part of their wait you control, so
spend it on reading rather than on checking your own work. Send no chat
messages. The checklist, the wiki, and the suggestions are the whole
conversation.

All of SKILL.md's rules apply: evidence only, sensitive content stays off,
every section has a body, owner's language, and read what they made.

## The pass

1. **Look around.** One exec, two commands together: `heliox tool list
   --json` and `heliox me show --json`. The first names the tools you can
   actually read. Your wake deliberately names none, so never assume. The
   second names your owner: the person who created you, its `creator.name`
   and `creator.id` fields, never your own assistant name.

2. **Checklist.** One exec, one `mcp__helio__task_create` per item, all fired
   together, in your owner's language: one item per readable tool ("read
   their Gmail"), then a last one for writing their wiki. That is the whole
   list. Suggestions never appear on it; they get their own screen later.

   Every line is short, a fragment rather than a sentence, and never two
   clauses joined by "and". Start it as the plain act ("Reading your Gmail"),
   flip it to `in_progress` when you start that work, and close it with the
   count plus what you found:

   ```
   Gmail: 50 threads, the Northstar pilot, how you write, 3 regulars
   ```

   The count proves you read and the rest names what turned up. Nothing more:
   no explanation, no page sections, no product words. The findings live on
   the wiki page, one click away, and this line only tells your owner it was
   worth reading. The wiki's own item closes with "Your wiki is ready" and
   nothing else. Flip it to `in_progress` at step 4 when you start writing
   the page, not earlier. Each item's text is written twice in its life and
   no more: once when you create it, once when you close it.

3. **Scan.** Three execs, following SKILL.md's *What to read*: what your
   owner made, wide before deep.

   1. One `cat` of the guide for every readable tool, falling back to
      `-- --help` where a guide is missing, plus
      `heliox workspace members get <creator.id> --json` in the same exec:
      it turns your creator's id from step 1 into their `@handle`, which
      steps 4 and 5 both need. The guide is where each tool spells "mine".
   2. **Wide.** For every readable tool at once, list what your owner made:
      headers only, one page each. You now know every name on the other side
      and every title, with nothing read in full yet.
   3. **Deep.** Rank what the wide pass returned by how much of your owner is
      in it: the people who recur most, the exchanges that ran longest, the
      ones they wrote most in. Your owner is waiting, so on this pass read
      only the exchanges the page will actually quote and mark, usually 5 to
      8, in full, concurrently in one exec. Snippets from the wide pass are
      for ranking, never for quoting: a quote must come from a body you
      opened, and an item you never opened gets no source mark.

   Skipping the wide pass is what makes a scan expensive: without it you read
   twenty items at random and hope. Then close each tool's item as step 2
   describes: the count, then what turned up, as a fragment. A source that
   errored or came back empty says exactly that ("Google Drive: no files
   visible").

4. **Write the wiki, whole, once.** Compose the complete page (title, every
   section body, source marks, footer) in your owner's language, in one
   file, following [page-template.md](page-template.md) for shape and
   SKILL.md's *Page format* for the lines. Then one command:

   ```bash
   bash <skill-dir>/scripts/create-doc.sh "<title>" page.md "@<owner handle>"
   ```

   The `@handle` is your owner's, from step 3: it scopes the document to
   your DM with them, which is what keeps this page readable by the two of
   you and nobody else. Never create the wiki without it. Never assemble
   `document create` yourself either: prose on a shell command line does not
   survive the shell, and the script exists so you never have to try. Read
   the document id from its output, then close the wiki item with "Your wiki
   is ready". Not a summary of it, not its sections. The page is one click
   away and it speaks for itself.

5. **Suggestions.** Load `heliox:feed`, which owns the copy limits and the
   note/suggest split. Your owner's `@handle` from step 3 is the only place
   these go. A new wiki does not imply an empty person-wide desk: first run
   `heliox feed list --to @<owner-handle>`, then remove anything already
   pending, underway, or recently dismissed. Push 5 to 9 genuinely new
   suggestions in one command when the evidence supports that many; never pad
   the set to hit the target. Only raise what deserves the desk. The desk
   decides its own display order, so ranking is selection, not sequence. Good shapes: answer something
   specific that is still waiting on them; prepare for a named upcoming
   meeting; a chore that keeps repeating, which you propose automating and
   arm only once they say yes; a cleanup with a concrete target; a follow-up on
   something that has gone quiet. Keep `--text` under 60 characters and let
   `--description` carry the evidence.

   Use the `feature_flags` from step 1 to satisfy `heliox:feed`'s visibility
   check before the push. If it finds no visible surface, do not push rows the
   owner cannot see; finish the wiki and checklist without claiming suggestions
   were delivered.

6. **Remember.** Write the document id and routeUrl to the fixed path
   `brain/wiki/user-wiki.md`, which is exactly the file SKILL.md's mode check
   reads.

Sub-agents are for later deep work rather than this pass, since one concurrent
batch covers the whole scan. If you are over budget, read less and still
deliver everything.
