# Bluesky (`heliox tool bluesky -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Bluesky is a
**flat provider**: everything after `--` is the Bluesky tool's own CLI,
speaking the AT Protocol (XRPC) with the connected account's app-password
session.

```bash
heliox tool bluesky [--account <key>] -- <resource> <verb> [flags...]
```

Every leaf takes `--json`. Run `-- <command> --help` for the full flag surface.

## The identity model (handles, DIDs, and at:// URIs)

Three kinds of handle flow through Bluesky; pass them back verbatim, never
invent them:

- A **handle** is `alice.bsky.social`: human-readable, can change.
- A **DID** is `did:plc:...`: the stable account key. Anywhere a command takes
  `--actor`, either a handle or a DID works.
- An **`at://` URI** (`at://<did>/app.bsky.feed.post/<rkey>`) plus a **`cid`**
  identify a specific post/record. `post create`, `like`, and `repost` echo the
  `uri`/`cid` they produce. Keep them to reply to, delete, like, or repost that
  item later.

## Writing posts

Rich text is automatic: pass plain `--text` and the tool detects links and
`#hashtags` and computes the byte-offset facets for you. `@mentions` are
resolved best-effort (an unresolvable handle is left as plain text; a post
never fails over a mention).

```bash
heliox tool bluesky -- post create --text "Shipping today https://helio.im #ai"
heliox tool bluesky -- post create --text "reply text" --reply-to at://did:plc:.../app.bsky.feed.post/...
heliox tool bluesky -- post create --text "quote text" --quote at://did:plc:.../app.bsky.feed.post/...
heliox tool bluesky -- post create --text "look" --image ./cat.png --alt "a cat on a keyboard"
```

Images: up to 4 per post via repeated `--image`; give each a matching `--alt`
in the same order (alt text is an accessibility requirement; an empty alt
warns). `--lang en` tags the post language.

```bash
heliox tool bluesky -- post get    --uri at://.../app.bsky.feed.post/...   # a post + thread root
heliox tool bluesky -- post delete --uri at://.../app.bsky.feed.post/...   # your own post
```

## Reading and searching

```bash
heliox tool bluesky -- timeline [--limit N] [--cursor C]         # your home timeline
heliox tool bluesky -- feed author --actor <handle|did> [--limit N]
heliox tool bluesky -- search posts  --q "..." [--limit N] [--cursor C]
heliox tool bluesky -- search actors --q "..." [--limit N]
heliox tool bluesky -- profile get   --actor <handle|did>
heliox tool bluesky -- notifications list [--limit N]            # mentions, replies, likes, follows
```

Reads are one page; pass the returned `cursor` back as `--cursor` for the next
page. Prefer `notifications list` over repeated searches for "what engagement
did I get": it is the lowest-cost path.

## Engaging

```bash
heliox tool bluesky -- like   --uri at://.../app.bsky.feed.post/... --cid <cid>
heliox tool bluesky -- repost --uri at://.../app.bsky.feed.post/... --cid <cid>
heliox tool bluesky -- follow   --actor <handle|did>
heliox tool bluesky -- unfollow --uri at://<you>/app.bsky.graph.follow/<rkey>
```

`like`/`repost` need both the target post's `uri` and `cid` (from a read
result). `unfollow` deletes the follow **record**: pass the `uri` that
`follow` returned, not the followed actor's handle.

## Connecting

Bluesky uses an **App Password**, not OAuth. Ask the user to generate one in
Bluesky Settings → App Passwords (never their main password), then connect with
`heliox tool bluesky auth`. The credential is entered as
`<handle-or-email>:<app-password>`; Helio verifies it by opening a session and
storing it encrypted.

`heliox tool bluesky -- whoami` confirms the connected account (handle + DID).
