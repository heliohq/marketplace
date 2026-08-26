# Buffer (`heliox tool buffer -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Buffer is a
**flat provider**: everything after `--` is Buffer's own CLI, speaking the
Buffer GraphQL API (`https://api.buffer.com`) with the connected account's
OAuth token. Use it to draft, schedule, and publish social-media posts across
the channels connected in the user's Buffer account.

```bash
heliox tool buffer [--account <key>] -- <resource> <verb> [flags...]
```

Resources: `account`, `org`, `channel`, `post`, `idea`. Every command prints one
JSON object; errors go to stderr with a non-zero exit.

## The mental model (account → organizations → channels → posts)

Buffer nests everything under the account. One account has one or more
**organizations** (workspaces); each organization owns the connected
**channels** (a Twitter/LinkedIn/Instagram/... profile), and posts and ideas
belong to an organization/channel. Most reads are **organization-scoped**, so
resolve the org id first:

```bash
heliox tool buffer -- account get            # id, email, and the organizations list
heliox tool buffer -- org list               # just the organizations
heliox tool buffer -- channel list --org <org-id>   # channels you can post to
```

`channel list` returns each channel's `id`, `name`, and `service`: the
`id` is what `post create --channel` takes.

## Reading posts

```bash
heliox tool buffer -- post list --org <org-id> \
  [--channel <channel-id>] [--status <status>] [--first 20] [--after <cursor>]
```

`--org` is **required**; `--channel` and `--status` are optional filters. The
result is a Relay page: `{"posts":[{id,text,createdAt,channelId}], "pageInfo":{
startCursor,endCursor,hasNextPage}}`. To page, pass the returned
`pageInfo.endCursor` as the next `--after`. `--status` (e.g. `sent`, `draft`)
passes straight through to Buffer's `PostStatus` filter: Buffer validates the
value, so an unknown status surfaces as an API error rather than a silent empty
page.

## Writing

```bash
# Add to the channel's queue (default scheduling)
heliox tool buffer -- post create --channel <channel-id> --text "..."

# Schedule at a specific time (ISO-8601 UTC)
heliox tool buffer -- post create --channel <channel-id> --text "..." \
  --mode customScheduled --due-at 2026-08-01T15:00:00Z

# Save a draft instead of queuing/publishing
heliox tool buffer -- post create --channel <channel-id> --text "..." --draft

heliox tool buffer -- post edit   --id <post-id> [--text "..."] [--mode customScheduled --due-at <ts>]
heliox tool buffer -- post delete --id <post-id>
```

`--mode` is `addToQueue` (default) or `customScheduled`; `customScheduled`
**requires** `--due-at`. Media and rich attachments are passed as raw Buffer
JSON via `--assets-json` / `--metadata-json` (validated as JSON before send).
Buffer rejects a post that carries both uploaded videos (`assets.videos`) and a
per-service link attachment (`metadata.<service>.linkAttachment`): supply only
one, or the command fails with a usage error before any API call.

## Ideas

Ideas live on an **organization**, not a channel; they are the Buffer content
backlog, not scheduled posts:

```bash
heliox tool buffer -- idea create --org <org-id> --text "..." [--title "..."]
```

## Footguns

- **Everything read is org-scoped**: `channel list`, `post list`, and
  `idea create` all require `--org`. If you only hold a channel id, run
  `account get` (or `org list`) first to get the organization id.
- **`--due-at` is ISO-8601 UTC** and only meaningful with
  `--mode customScheduled`; passing it with the default queue mode is ignored by
  Buffer.
- **Public beta API**: Buffer's GraphQL API is in public beta; transient schema
  or availability changes surface as explicit API errors (never a silent empty
  result).

## Safety

Creating, editing, and deleting posts are **outward-facing publishing actions**
on the user's real social accounts. Follow the sensitive-operation rule from
`../SKILL.md`: confirm with the user before the first publish/schedule in
a session, and never post content the user has not sanctioned. Prefer `--draft`
or an explicit `--due-at` when the user has not asked to publish immediately.
