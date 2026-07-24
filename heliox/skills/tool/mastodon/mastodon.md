# Mastodon (`heliox tool mastodon -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Mastodon is a
**flat provider**: everything after `--` is the Mastodon tool's own CLI,
speaking the Mastodon REST API with the connected account's access token.

```bash
heliox tool mastodon [--account <key>] -- <command> [flags...]
```

Mastodon is **federated** — there is no single server. The connected account is
one identity on one instance (e.g. `mastodon.social`, `fosstodon.org`, a
self-hosted server); its `--account` key is that instance's URL. All requests
go to that instance automatically; you never pass the instance or the token.

## Connecting

There is no OAuth screen. On the user's own instance they open **Settings →
Development → New application**, request **read + write + follow** scopes, and
copy **"Your access token"**. They paste the **instance URL and that token,
separated by a space** (e.g. `https://mastodon.social <token>`) into the connect
form. The token does not expire; it is revoked only when the user deletes the
application. Point the user at <https://docs.joinmastodon.org/client/token/>.

## Identity and reading

```bash
heliox tool mastodon -- whoami                         # the connected account
heliox tool mastodon -- timeline home [--limit N] [--cursor C]
heliox tool mastodon -- timeline public [--local]      # federated, or --local to this instance
heliox tool mastodon -- timeline tag <hashtag>
heliox tool mastodon -- account get <@user@instance | id>
heliox tool mastodon -- account posts <@user@instance | id>
heliox tool mastodon -- search --q "..." [--type accounts|hashtags|statuses]
heliox tool mastodon -- notifications list             # mentions, follows, boosts, favourites
heliox tool mastodon -- post get --id <id>             # status + its thread (ancestors/descendants)
```

Speak **handles**, not numeric ids: `account get`, `account posts`, `follow`,
and `unfollow` accept a human `@user@instance` handle and resolve it for you.
Post `content_text` is the HTML content already stripped to plain text, so you
read posts without parsing markup. List commands return a `cursor` — pass it
back as `--cursor` to page to older items.

## Writing

```bash
heliox tool mastodon -- post create --text "..." \
    [--reply-to <id>] [--cw "spoiler text"] \
    [--visibility public|unlisted|private|direct] [--lang en]
heliox tool mastodon -- post create --text "with a photo" --image ./pic.png --alt "描述"
heliox tool mastodon -- post delete --id <id>
heliox tool mastodon -- favourite --id <id>            # like a status
heliox tool mastodon -- boost --id <id>                # reblog a status
heliox tool mastodon -- follow <@user@instance | id>   # unfollow: same, `unfollow`
```

- **Reply = a full status** (a `--reply-to`) — there is no separate comment
  entity; reply to a status id to comment on it, and read a thread with
  `post get --id <id>` (returns ancestors + descendants).
- **Idempotent posts**: `post create` is safe to retry — identical parameters
  within Mastodon's window return the already-created status instead of
  double-posting.
- **Images**: up to 4 per post; always pass `--alt` (accessibility — the tool
  warns when it is missing). Uploads that the server processes asynchronously
  are waited out before the post is created.

## Escape hatch

For endpoints without a first-class command (lists, bookmarks, filters,
scheduled statuses, admin):

```bash
heliox tool mastodon -- api GET /api/v1/bookmarks
heliox tool mastodon -- api POST /api/v1/lists --body '{"title":"Friends"}' --query foo=bar
```

The `Authorization` header is injected and cannot be overridden.

## Footguns

- **One connection per instance per assistant** (this version): two accounts on
  the same server collapse to one connection; different instances are naturally
  distinct.
- **Handles are per-instance**: a numeric id from one instance means nothing on
  another — always resolve via the `@user@instance` handle.
- **Visibility matters**: `direct` is a DM-style post to mentioned accounts;
  `private` is followers-only. Default (omit `--visibility`) uses the account's
  configured default.

## Safety

Posting, replying, boosting, favouriting, and following are **public,
outward-facing actions** on the user's real Mastodon account across an open
federation. Follow the sensitive-operation rule from `../SKILL.md`:
confirm with the user before first-of-kind outward actions in a session, and
never post content the user has not sanctioned.
