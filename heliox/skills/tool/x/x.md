# X (`heliox tool x -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. X is a
**flat provider**: everything after `--` is the X tool's own CLI, speaking
X API v2 with the connected account's OAuth user token.

```bash
heliox tool x [--account <key>] -- <resource> <verb> [flags...]
```

Resources: `me`, `user`, `post`, `timeline`, `repost`, `like`, `follow`,
`media`, `dm`. Run `-- <resource> --help` for the full flag surface.

## The mental model (comments are replies, replies are posts)

X has no separate "comment" entity. A comment **is** a reply, and a reply
**is** a full post (it can be liked, reposted, replied to, quoted). Everything
comment-shaped therefore lives under `post`:

```bash
heliox tool x -- post reply <post-id> --text "..."   # write a comment
heliox tool x -- post replies <post-id>              # read a post's comments
heliox tool x -- post hide <reply-id>                # moderate: hide a reply under YOUR post
heliox tool x -- post unhide <reply-id>
```

All posts in one reply tree share one conversation; `post replies` returns the
whole conversation, not just direct children — reconstruct nesting from each
item's `referenced_tweets` (`type: replied_to`).

## Reading engagement on your own posts (do this the cheap way)

For "what new comments/mentions did I get", prefer the incremental mentions
timeline over repeated searches — it is the lowest-cost read path and
`--since-id` makes polling exact:

```bash
heliox tool x -- timeline mentions --since-id <last-seen-post-id>
```

Remember the newest returned post id and pass it as the next `--since-id`.
`--since-id` works the same on `timeline user`, `timeline home`,
`post search`, and `post replies`.

Who engaged:

```bash
heliox tool x -- post liking-users <post-id>
heliox tool x -- post reposters <post-id>
heliox tool x -- post quotes <post-id>
heliox tool x -- user followers            # defaults to the connected account
heliox tool x -- user following --user-id <id>
```

## Pagination

Every X list or search command returns one page. Its continuation marker is
`meta.next_token`; pass it back as `--next-token <meta.next_token>` when another
page is needed.

Do not pipe a paginated response through `head` or parse only `data` before
checking `meta`. For incremental reads, `--since-id` narrows the window but
does not replace pagination.

## Writing

```bash
heliox tool x -- post create --text "..." [--media-id <id>]...   # new post
heliox tool x -- post quote <post-id> --text "..."               # quote-post with comment
heliox tool x -- post thread --text "1/" --text "2/"             # self-reply thread
heliox tool x -- repost create <post-id>
heliox tool x -- like create <post-id>       # like / unlike: like delete
heliox tool x -- follow create <user-id>     # follow / unfollow: follow delete
```

Images go through `media upload` first; pass the returned media id via
`--media-id`.

## Footguns

- **7-day window**: `post replies` and `post search` ride X's recent search —
  they cannot see posts older than 7 days. `post get <id>` still works on any
  age; there is no full-archive access on our API plan.
- **`post hide` only works on replies to the connected account's own posts** —
  403 otherwise.
- **Batch reads**: `post get` accepts up to 100 ids in one call — prefer one
  batched call over a loop.
- **Search limit floor**: `post search` / `post replies` `--limit` is 10-100
  (the API rejects smaller pages); user-list commands are 1-100, follower
  lists 1-1000.
- **`timeline home` is always the connected user** — no `--user-id` there.
- **DM coverage**: `dm` reads up to 30 days of legacy DM events; it does not
  read encrypted XChat message history. Delivery to some accounts may be
  restricted.

## Safety

Posting, replying, quoting, reposting, liking, following, and DMs are all
**public or outward-facing actions** on the user's real X account: follow the
sensitive-operation rule — confirm with the user before first-of-kind outward
actions in a session, and never post content the user has not sanctioned.
