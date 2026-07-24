# Typefully (`heliox tool typefully -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Typefully is a
**flat provider** (not grouped like `google`): everything after `--` is the
typefully tool's own CLI. It wraps the Typefully **v2** REST API — draft,
schedule and publish social posts/threads to X, LinkedIn, Threads, Bluesky and
Mastodon, inspect the queue, tag drafts, and pull basic X analytics.

```bash
heliox tool typefully [--account <key>] -- <group> <verb> [flags...]
```

## Connect

Typefully uses a **user-scoped API key**, not OAuth. Ask the user to connect
(you cannot authorize for them), then they paste a key created in Typefully
**Settings → API** (the `?settings=api` panel). Enabling **Development mode**
there surfaces the social-set / draft / media IDs you'll work with. Any key made
today is a **v2** key (v1 is sunset); the tool sends `Authorization: Bearer`.

## Two things to get right first

### 1. Discover the social set before anything else

Every command except `me` is scoped to a **social set** (`--social-set <id>`).
Start by listing them and take the id:

```bash
heliox tool typefully -- me                         # who the key belongs to
heliox tool typefully -- social-set list            # take /results/0/id (or the matching account)
```

Pass that id as `--social-set` to every other command.

### 2. `publish-at now` is async, and `finished` ≠ success

Creating a draft with `--publish-at now` returns `201` immediately but publishes
**asynchronously**. The response `publish_state` starts non-terminal
(`null` → `in_progress` → `finished`). Poll the draft until it is `finished`:

```bash
heliox tool typefully -- draft create --social-set <id> --text "Launch is live 🚀" --publish-at now
heliox tool typefully -- draft get --social-set <id> --id <draft>   # repeat until publish_state == "finished"
```

`finished` only means the job is **done, not that it succeeded.** After it is
finished, read the draft's `status` (`published` vs `error`) **and** the
per-platform published URLs (`x_published_url`, `linkedin_published_url`,
`mastodon_published_url`, …; `null` = that platform did not post) to tell a full
success from a partial/failed publish. Report **which** platform(s) failed —
never assume a `finished` job published everywhere.

`--publish-at next-free-slot` (queue) and `--publish-at <ISO-8601>` (a future
datetime with timezone) **schedule** instead — no polling needed. Omit
`--publish-at` to save a plain draft.

## Core commands

```bash
# Drafts (the core)
heliox tool typefully -- draft list   --social-set <id> [--status scheduled --tag <t> --order-by <o> --limit N --offset N]
heliox tool typefully -- draft get    --social-set <id> --id <draft> [--exclude-comment-markers]
heliox tool typefully -- draft create --social-set <id> --text "post 1" --text "post 2" --platform x --platform linkedin --publish-at next-free-slot
heliox tool typefully -- draft update --social-set <id> --id <draft> --data '{"publish_at":"2026-08-01T09:00:00Z"}'
heliox tool typefully -- draft delete --social-set <id> --id <draft>

# Tags, queue, analytics
heliox tool typefully -- tag list     --social-set <id>
heliox tool typefully -- tag create   --social-set <id> --name launch
heliox tool typefully -- queue view   --social-set <id> --start-date 2026-08-01 --end-date 2026-08-31   # window <= 62 days
heliox tool typefully -- queue schedule-get --social-set <id>
heliox tool typefully -- queue schedule-set --social-set <id> --data '<json>'                            # needs ADMIN
heliox tool typefully -- analytics posts     --social-set <id> --platform x [--start-date --end-date --include-replies]
heliox tool typefully -- analytics followers --social-set <id> --platform x

# Media, LinkedIn, comments
heliox tool typefully -- media upload  --social-set <id> --file ./image.png     # returns media_id; pass to draft create --media-id
heliox tool typefully -- media status  --social-set <id> --id <media>
heliox tool typefully -- linkedin resolve-org --social-set <id> --organization-url <url>
heliox tool typefully -- comment threads      --social-set <id> --id <draft>
```

## Creating drafts: typed flags vs `--data`

`draft create` takes **either** the thin convenience flags **or** a raw
`--data '<json>'` body — they are **mutually exclusive** (usage error, exit 2).

- Convenience (the 80% path): repeatable `--text` builds a thread (one post per
  flag), `--platform` (repeatable, default `x`) chooses targets, `--publish-at`
  schedules/publishes, `--media-id` (repeatable) attaches media to the first
  post. The tool assembles the verified `platforms` body:
  `{"platforms":{"x":{"enabled":true,"posts":[{"text":"…"}]}}}`.
- `--data '<raw json>'` — for anything richer (per-platform post overrides,
  titles, tags, `rules`). Send the exact v2 body.

`draft update` and `queue schedule-set` take `--data '<json>'` only.

## Errors and exit codes

- `0` success; `2` usage/flag errors (bad flag combo, invalid `--data` JSON,
  missing required flag); `1` runtime/API errors.
- A `401` (or auth-shaped `403`) means the **key is invalid** — ask the user to
  reconnect.
- A **permission** `403` (e.g. "Insufficient permissions") means the key is
  valid but lacks the required access level on that social set — creating needs
  WRITE, scheduling/immediate publish needs PUBLISH, `queue schedule-set` needs
  ADMIN. This is **not** a reconnect; tell the user their key needs a higher
  access level.
- A `429` is a rate limit — back off, do not auto-retry.

Every command prints the provider's JSON verbatim on stdout. For anything not
covered here, `heliox tool typefully -- --help` (and `<group> --help`) is the
reference.
