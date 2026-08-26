# Reddit (`heliox tool reddit -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Reddit is a
**flat provider**: everything after `--` is the Reddit tool's own CLI, speaking
the Reddit Data API (`https://oauth.reddit.com`) with the connected account's
OAuth user token.

```bash
heliox tool reddit [--account <key>] -- <resource> <verb> [flags...]
```

Resources: `me`, `subreddit`, `search`, `post`, `comment`, `user`, `inbox`,
`message`, `subs`. Run `-- <resource> --help` (or `-- <resource> <verb> --help`)
for the full flag surface. Add `--json` for structured output.

## Output shape (read this before parsing)

Reddit wraps everything in `Listing`/`kind`+`data` envelopes; this tool strips
them. Under `--json`:

- **Listing commands** (`subreddit posts`, `search`, `user posts|comments`,
  `inbox list`, `subs list`) emit **JSONL** (one flat object per line)
  followed by a final `{"after":"t3_…"}` line **only when another page exists**.
  Pass that value back as `--after` to page. Posts are
  `{id, fullname, title, author, subreddit, score, num_comments, created_utc,
  permalink, url, selftext}`; comments are
  `{id, fullname, author, body, score, parent_id, depth, created_utc}`.
- **`post comments`** flattens the reply tree into JSONL with a `depth` field;
  unexpanded branches surface as `{"kind":"more","count":N,"parent_id":…}`
  stubs rather than being silently dropped: fetch them separately if needed.
- **Write commands** echo the created/affected thing (`fullname`, `permalink`).

`fullname` is Reddit's global id with a type prefix: `t1_` comment, `t3_`
post/link, `t4_` message, `t5_` subreddit. `edit`, `delete`, `comment create
--parent`, and `inbox mark-read` all take a **fullname**; `post get`/`post
comments` accept either the bare id36 or the `t3_` form.

## Reading & research

```bash
heliox tool reddit -- me                                   # who am I
heliox tool reddit -- subreddit about golang               # rules-lite metadata
heliox tool reddit -- subreddit rules golang               # posting rules: check BEFORE participating
heliox tool reddit -- subreddit posts golang --sort top --time week --limit 25
heliox tool reddit -- search --query "vector db" --subreddit golang --sort new
heliox tool reddit -- post get <id>                        # a single post
heliox tool reddit -- post comments <id> --sort top        # the discussion tree
heliox tool reddit -- user about spez
heliox tool reddit -- subs list                            # my subscriptions
```

`subreddit posts --sort` is `hot|new|top|rising` (default `hot`); `--time`
(`hour|day|week|month|year|all`) only applies to `top`. `search --sort` is
`relevance|hot|top|new|comments`.

## Inbox (community-manager loop)

```bash
heliox tool reddit -- inbox list --filter unread          # all | unread | mentions
heliox tool reddit -- inbox mark-read t1_abc t4_def       # one or more fullnames
```

## Writing

```bash
heliox tool reddit -- post create --subreddit golang --title "…" --text "body (markdown)"
heliox tool reddit -- post create --subreddit golang --title "…" --url https://…   # link post
heliox tool reddit -- comment create --parent <fullname> --text "…"                # reply
heliox tool reddit -- post edit <t3_fullname> --text "…"     # your own self-post
heliox tool reddit -- comment edit <t1_fullname> --text "…"
heliox tool reddit -- post delete <t3_fullname>
heliox tool reddit -- comment delete <t1_fullname>
```

There is **no** command for sending a private message. Reading the inbox is
supported (`inbox list`, including `--filter mentions` for replies and
mentions on what you posted), but composing a DM to someone is not something
this tool does: say so plainly if asked rather than looking for a flag.

`post create` takes **exactly one** of `--text` (self-post) or `--url` (link).

## Footguns

- **No voting.** There is deliberately no upvote/downvote command: Reddit's
  rules require votes to be cast by humans, so an agent must not vote.
- **Search cannot see comments and has no date range.** `search` matches posts
  only; to read comments you must open a post with `post comments`. There is no
  before/after-date filter: use `--sort new` / `--time` and page with
  `--after`.
- **Rate limit: 100 requests/minute per app**, averaged over 10 minutes. On a
  429 the tool surfaces `remaining=`/`reset=` and fails: do **not** retry in a
  loop; back off past the reset window.
- **Check the subreddit rules before posting.** Many subreddits restrict
  self-promotion, link posts, or account age; `subreddit rules <name>` is the
  cheap pre-flight. A rule violation comes back as a write error (e.g.
  `SUBREDDIT_NOEXIST`, `NO_SELFS`, `SUBREDDIT_NOTALLOWED`).
- **Edit is self-text only.** `post edit` works on your own self-posts, not link
  posts and not other people's content.
- **`--limit` is 1-100** on every listing (Reddit's page ceiling).
- **`more` stubs are not comments.** In a big thread, `post comments` returns
  `{"kind":"more",…}` placeholders for collapsed branches: treat them as "there
  is more here", not as content.

## Safety

Submitting posts, replying, sending messages, and editing/deleting are all
**public or outward-facing actions** on the user's real Reddit account: follow
the sensitive-operation rule from `../SKILL.md`; confirm with the user
before first-of-kind outward actions in a session, respect each subreddit's
rules, and never post content the user has not sanctioned.
