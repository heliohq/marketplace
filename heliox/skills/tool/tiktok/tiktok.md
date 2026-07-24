# TikTok (`heliox tool tiktok -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. TikTok is a
**flat provider**: everything after `--` is the TikTok tool's own CLI, speaking
the TikTok API v2 (Display API + Content Posting API) with the connected
creator account's OAuth user token.

```bash
heliox tool tiktok [--account <key>] -- <resource> <verb> [flags...]
```

Resources: `user`, `video`, `creator`, `post`. Run `-- <resource> --help` for
the full flag surface. Every command emits the provider's response with the
`{data, error}` envelope unwrapped to a flat object.

## Reading the account and its videos

```bash
heliox tool tiktok -- user info                       # the connected creator
heliox tool tiktok -- user info --fields open_id,display_name,follower_count
heliox tool tiktok -- video list --max-count 20       # one page of videos
heliox tool tiktok -- video list --cursor <ts>        # next page (UTC unix ms)
heliox tool tiktok -- video query --ids id1,id2       # specific videos by id
```

`user info` defaults to basic-scope fields (`open_id,union_id,avatar_url,
display_name`); request `follower_count`, `likes_count`, `bio_description`,
etc. via `--fields` — those need the profile/stats scopes granted at connect.

## Posting a video (do the prerequisite first)

Direct Post publishes straight to the profile. **Always call `creator info`
first** — it returns the account's allowed `privacy_level_options` and limits,
and the privacy level you post with must be one of them:

```bash
heliox tool tiktok -- creator info
heliox tool tiktok -- post video --url https://cdn.example/clip.mp4 \
  --title "..." --privacy SELF_ONLY
heliox tool tiktok -- post video --file ./clip.mp4 --title "..." --privacy PUBLIC_TO_EVERYONE
heliox tool tiktok -- post status --publish-id <id>   # poll processing status
```

- `--url` hands TikTok a public URL to pull the video from (simplest).
  `--file` uploads a local file (single-chunk PUT after init).
- Direct post **requires** `--privacy`. Use `--draft` to skip publishing and
  drop the video into the creator's TikTok inbox to finish in the app — a draft
  upload takes no privacy level.
- `post video` returns a `publish_id`; posting is asynchronous, so poll
  `post status --publish-id <id>` until it reports done.

## Footguns

- **Fields are scope-gated**: requesting `follower_count` / `bio_description`
  without the `user.info.stats` / `user.info.profile` scope errors. Stick to the
  default fields unless the account granted more at connect.
- **Direct Post needs an audited app**: `video.publish` / `video.upload` only
  work against arbitrary creators once TikTok has audited the app; on an
  unaudited/sandbox app, posts are forced to private and limited to test users.
- **`--max-count` is 1-20**; the cursor is a UTC unix millisecond timestamp,
  not an opaque token — pass the `cursor` returned by the previous page.
- **The acting account is the bearer token's**; `user info` has no target flag.

## Safety

Posting a video (direct post or draft), whether to the public or to the
creator's own inbox, is an **outward-facing action on the user's real TikTok
account**: follow the sensitive-operation rule from `../SKILL.md` —
confirm with the user before the first post in a session, and never publish
content the user has not sanctioned.
