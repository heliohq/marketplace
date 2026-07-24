# Instagram (`heliox tool instagram -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Instagram is a
**flat provider** (not grouped like `google`): everything after `--` is the
instagram tool's own CLI. One connection is **one Instagram professional
account** (Business or Creator) — `/me` is that account, so there is no account
selector inside commands.

```bash
heliox tool instagram [--account <key>] -- <group> <verb> [flags...]
```

This wraps the **Instagram API with Instagram Login** (`graph.instagram.com`),
not the Facebook-Login path. All output is JSON.

## Command surface

```bash
# Account
heliox tool instagram -- account get                       # profile + follower/media counts

# Media (read)
heliox tool instagram -- media list [--limit N] [--after CURSOR] [--fields ...]
heliox tool instagram -- media get <media_id> [--fields ...]
heliox tool instagram -- media insights <media_id> [--metrics reach,likes,comments,saved,shares]

# Account insights
heliox tool instagram -- insights [--metrics reach,follower_count] [--metric-type total_value] [--period day] [--since UNIX] [--until UNIX]

# Comments (community management)
heliox tool instagram -- comment list <media_id> [--fields ...]
heliox tool instagram -- comment reply <comment_id> --message "..."
heliox tool instagram -- comment hide <comment_id> --hidden true|false
heliox tool instagram -- comment delete <comment_id>
```

## Publishing is a 3-step async flow — do not expect one call

Instagram publishing is **container-based and asynchronous**. You create a
container, Instagram processes the media in the background (downloads the URL,
transcodes video, makes thumbnails), and only once it is `FINISHED` can you
publish it. There is no single "post" verb — you drive the wait:

```bash
# 1. Create a container from a PUBLICLY reachable media URL -> returns {"id": "<container_id>"}
heliox tool instagram -- publish create --image-url https://.../photo.jpg --caption "..."
heliox tool instagram -- publish create --video-url https://.../reel.mp4 --media-type REELS --caption "..."

# 2. Poll until FINISHED (IN_PROGRESS -> FINISHED; ERROR/EXPIRED exit non-zero)
heliox tool instagram -- publish status <container_id>

# 3. Publish the FINISHED container -> returns the published media id
heliox tool instagram -- publish finish <container_id>
```

Rules the tool surfaces rather than hides:

- **Media must be at a publicly reachable URL** at publish time (Instagram
  fetches it server-side). A localhost or auth-gated URL fails. For a local
  file or chat attachment, mint one: `heliox blob put <file>` → helio:// URI,
  then `heliox blob share <uri>` → short-lived public URL to pass as
  `--video-url`/`--image-url`. Run `publish create` right after `share` —
  the URL expires (~1h), and Instagram fetches during container processing.
- **Containers expire after 24h.** `publish status` returns `EXPIRED` for a
  stale one — recreate it.
- **`--media-type`** is `IMAGE` (feed photo, default for `--image-url`),
  `REELS`, or `STORIES` (video, use `--video-url`).
- **50 published posts / 24h** per account (Instagram cap).
- Poll `publish status` yourself between create and finish — do not fire
  `finish` on a non-`FINISHED` container.

## Account insights are version-sensitive

The connection is pinned to a fixed Graph version (v23). Instagram deprecates
insight metrics per version, so:

- The built-in default (`reach,follower_count`) targets the pinned version;
  `profile_views` was deprecated (use `views` if you want views), and other
  metrics may come and go — pass `--metrics ...` explicitly when you need
  something specific.
- Several account-level metrics on the pinned version require
  `--metric-type total_value`. If `instagram insights` returns a Graph error
  about `metric_type`, re-run with `--metric-type total_value`. Note that a
  time-series metric like `follower_count` is *not* a total_value metric, so
  don't mix the two in one call.

## Auth & footguns

- **Connections lapse at ~60 days.** The stored token is a ~60-day long-lived
  token and is **not** auto-refreshed today, so an idle connection eventually
  expires and needs a manual reconnect (`heliox tool instagram auth`). Treat a
  reconnect prompt as expected on a long-dormant account, not a bug.
- **Reconnect signal.** A `code:190` / HTTP 401 (`OAuthException`) means the
  token is expired or revoked — the command exits non-zero with a "reconnect"
  message. Ask the user to re-run `heliox tool instagram auth`; do not retry.
- **Personal accounts are unsupported** — the account must be a professional
  (Business or Creator) Instagram account.
- **DMs, mentions/tags, and hashtag search are not exposed** (deferred /
  unavailable on the Instagram-Login path).

For anything not covered here, `heliox tool instagram -- <group> --help`.
