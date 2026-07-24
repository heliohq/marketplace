# YouTube (`heliox tool youtube -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. YouTube is a
**flat provider** (not grouped like `google`): everything after `--` is the
youtube tool's own CLI, over the YouTube Data API v3.

```bash
heliox tool youtube [--account <key>] -- <resource> <verb> [flags...]
```

One connection = one Google account. A single Google login can own several
YouTube channels; `--mine` / `--channel <id>` at the verb layer picks among
them. Every command takes a persistent `--json` flag (structured output;
otherwise a compact human summary).

## The mental model (read this first)

- **`part` shapes every read.** The Data API hydrates only the resource
  sections you ask for (`snippet`, `statistics`, `contentDetails`, `status`,
  `replies`, …). The tool sends a sensible default per verb and lets `--part`
  override it — pass the API's own part names verbatim.
- **Quota is real.** Default project quota is 10,000 units/day. `search` costs
  **100 units**; most reads cost 1; writes ~50. A `403 quotaExceeded` is
  surfaced verbatim — there is no client-side retry. Prefer `videos mine`
  (uploads playlist, ~1–2 units) over `search` for "my videos".
- **Paging.** List verbs take `--max N` (1–50, default 5) and `--page <token>`,
  and echo `nextPageToken` for the next call.

## Core commands

### Channel & audience context

```bash
# your channel's lifetime stats (subscribers / views / videos)
heliox tool youtube -- channels get --mine --json
heliox tool youtube -- channels get --id UCxxxx,UCyyyy
heliox tool youtube -- channels get --for-handle @SomeHandle
```

`channels get` reports **lifetime** cumulative counts, not windowed
time-series analytics (that is a separate API, out of scope).

### Research / discovery

```bash
# search (100-unit cost) — ids come back flattened to a top-level id + kind
heliox tool youtube -- search --query "launch recap" --type video --max 5 --json
heliox tool youtube -- search --query "" --channel UCxxxx --order date

# a video's metadata + statistics
heliox tool youtube -- videos get --id VIDEO_ID,VIDEO_ID2 --json

# your own uploads (uploads-playlist path, complete + cheap — never search)
heliox tool youtube -- videos mine --max 20 --json
```

### Community management (the highest-frequency loop)

```bash
# top-level comment threads on a video (replies hydrated)
heliox tool youtube -- comments list --video VIDEO_ID --order time --json
# replies under one top-level comment
heliox tool youtube -- comments replies --parent COMMENT_ID
# reply / edit-your-own / delete
heliox tool youtube -- comments reply  --parent COMMENT_ID --text "Thanks for watching!"
heliox tool youtube -- comments update --id COMMENT_ID --text "fixed typo"
heliox tool youtube -- comments delete --id COMMENT_ID
# moderate: hold / publish / reject. --ban-author is valid ONLY with rejected.
heliox tool youtube -- comments moderate --id COMMENT_ID --status rejected --ban-author
```

### Playlist curation

```bash
heliox tool youtube -- playlists list --mine --json
heliox tool youtube -- playlists create --title "Best of Q3" --privacy unlisted
heliox tool youtube -- playlists update --id PLAYLIST_ID --description "curated"
heliox tool youtube -- playlists delete --id PLAYLIST_ID

heliox tool youtube -- playlist-items list   --playlist PLAYLIST_ID --json
heliox tool youtube -- playlist-items add    --playlist PLAYLIST_ID --video VIDEO_ID
# remove takes the playlistItem id (from `playlist-items list`), NOT the video id
heliox tool youtube -- playlist-items remove --id PLAYLIST_ITEM_ID
```

### Video metadata + ratings

```bash
# update is read-modify-write: it fetches the current snippet and merges your
# fields, so untouched required fields (title, categoryId) are preserved.
heliox tool youtube -- videos update --id VIDEO_ID --title "New title" --tags a,b,c
heliox tool youtube -- videos update --id VIDEO_ID --privacy unlisted
heliox tool youtube -- videos rate   --id VIDEO_ID --rating like   # like|dislike|none
```

### Subscriptions

```bash
heliox tool youtube -- subscriptions list --mine --json
```

## Footguns

- **`videos mine` is not `search`.** It resolves the uploads playlist
  (`channels.list` → `relatedPlaylists.uploads` → `playlistItems.list`): cheap,
  complete, immediately consistent. `search --forMine` would be 100 units,
  ~500-capped, and eventually-consistent (very recent uploads can be missing).
- **`playlist-items remove` needs the playlistItem id**, not the video id — the
  same video can appear multiple times, each with its own item id.
- **`--ban-author` only applies with `--status rejected`.** Any other status is
  rejected before the call (the API returns `400 banWithoutReject`).
- **No upload / no captions / no live / no Analytics.** This tool does not
  upload video files, manage captions/thumbnails, drive live broadcasts, or
  return windowed analytics — those are out of scope for v1.

## Safety

Replying to or moderating comments, and editing video/playlist metadata, are
outward-facing actions on the user's public channel — follow the
sensitive-operation rule in `../SKILL.md`: confirm before posting public
replies, rejecting/​banning commenters, or changing a video's privacy.
