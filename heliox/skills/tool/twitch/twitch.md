# Twitch (`heliox tool twitch -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Twitch is a
**flat provider**: everything after `--` is the Twitch tool's own CLI, speaking
the Helix API (`https://api.twitch.tv/helix`) with the connected account's OAuth
user token.

```bash
heliox tool twitch [--account <key>] -- <resource> <verb> [flags...]
```

Resources: `user`, `channel`, `stream`, `search`, `clip`, `video`, `follower`,
`subscriber`, `chat`. Run `-- <resource> --help` (or `-- <resource> <verb>
--help`) for the full flag surface. Output is always JSON; `--json` is accepted
for uniformity but is the default.

## Output shape (read this before parsing)

Helix wraps every response in a `data` array; this tool re-shapes it so you
don't have to:

- **List verbs** (`stream list`, `stream followed`, `search channels`,
  `clip list`, `video list`, `follower list`, `subscriber list`, `chatters`,
  and `user get` with more than one `--id`/`--login`) emit
  `{"data":[...],"cursor":"<next or empty>"}`. When `cursor` is non-empty, pass
  it back as `--after` to fetch the next page.
- **Single-object verbs** (`user get` for self / one lookup, `channel get`,
  `clip create`, `chat send`) emit the Helix object **unwrapped** from its
  `data[0]` array. A lookup that matched nothing emits `null`.
- **`channel update`** returns `{"updated":true,"broadcaster_id":"..."}` (Helix
  answers the PATCH with 204 No Content).

## "Self" is automatic

Channel-scoped verbs default `broadcaster_id` to the **connected account's own
channel**. The tool resolves your user id once (via Get Users) and caches it,
so you don't have to look it up first:

- `channel get`, `channel update`, `stream followed`, `clip create`,
  `follower list`, `chatters`, and `chat send` all target **you** by default.
- `subscriber list` and `chatters` are always keyed to you (Twitch only lets a
  broadcaster/moderator read their own).
- Pass `--broadcaster-id <id>` (or, where offered, `--login`) to target another
  channel instead.

## Reading & discovery (no extra scope)

```bash
heliox tool twitch -- user get                              # who am I (self)
heliox tool twitch -- user get --login ninja --login pokimane  # look up others
heliox tool twitch -- channel get                           # my title, game, tags, language
heliox tool twitch -- channel get --broadcaster-id 141981764
heliox tool twitch -- stream list --user-login shroud       # is a channel live?
heliox tool twitch -- stream list --game-id 509658 --first 20
heliox tool twitch -- search channels --query "speedrun" --live-only
heliox tool twitch -- clip list --broadcaster-id 141981764 --first 20
heliox tool twitch -- video list --user-id 141981764 --type archive
```

`clip list` and `video list` each require **exactly one** selector
(`--broadcaster-id` / `--game-id` / `--id` for clips; `--id` / `--user-id` /
`--game-id` for videos). Helix rejects zero or multiple.

## Curating the channel

```bash
# update stream metadata: send only the fields you want to change
heliox tool twitch -- channel update --title "Ranked grind" --game-id 509658
heliox tool twitch -- channel update --tags English --tags Speedrun   # replaces the full set
heliox tool twitch -- channel update --language en

# clip the live stream (self by default); returns the clip id + edit URL
heliox tool twitch -- clip create
```

`channel update` needs at least one of `--title` / `--game-id` / `--language`
/ `--tags` / `--delay`; passing `--game-id ""` clears the category. Requires the
`channel:manage:broadcast` scope; `clip create` requires `clips:edit`.

## Community & participation

```bash
heliox tool twitch -- stream followed                       # live channels I follow (user:read:follows)
heliox tool twitch -- follower list --first 100             # my followers (moderator:read:followers)
heliox tool twitch -- subscriber list                       # my subscribers (channel:read:subscriptions)
heliox tool twitch -- chatters                              # who's in my chat now (moderator:read:chatters)
heliox tool twitch -- chat send --message "Thanks for the raid!"   # (user:write:chat)
heliox tool twitch -- chat send --broadcaster-id 141981764 --message "gg" --reply-parent-message-id <msg-id>
```

## Footguns (where agents go wrong)

- **Ids, not names, for most filters.** `--game-id` / `--broadcaster-id` /
  `--user-id` are Twitch numeric ids, not display names. Resolve a login to an
  id with `user get --login <name>` (the returned `id`), or use the
  `--user-login` filters where a verb offers them (`stream list`).
- **`channel update` is a partial update.** Only the flags you pass are sent;
  omitted fields are left unchanged. Don't re-send the whole channel to change
  one field.
- **`--tags` replaces the entire tag set**, it does not append. Pass every tag
  you want to keep.
- **Pagination is cursor-based, not offset.** Page by feeding the response
  `cursor` back as `--after`; `--first` only sets page size (Helix max 100).
  A missing/empty `cursor` means the last page.
- **Follower / subscriber / chatter lists need you to be the broadcaster (or a
  moderator).** Reading another channel's followers or chatters will `401`/`403`
  unless the connected account has that role there.
- **Sending chat has eligibility rules.** `chat send` can be refused by Twitch
  (phone-verified account, channel chat settings, rate limits) even with the
  scope. Surface the Helix `message` on failure rather than retrying blindly.
- **`--account` when more than one Twitch account is connected.** A `409` lists
  the candidate account keys; re-run with `--account <key>` (before the `--`).

## Safety

- `chat send`, `clip create`, and `channel update` are outward-facing. They
  change what your audience sees or post under your name. Follow the sensitive-
  operation rule in [../SKILL.md](../SKILL.md) and confirm scope/target before
  writing to a channel you don't own.
