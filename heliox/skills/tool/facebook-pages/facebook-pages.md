# Facebook Pages (`heliox tool facebook-pages -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Facebook Pages
is a **flat provider**: everything after `--` is the tool's own CLI, speaking
the Facebook Graph API with the connected Facebook **user**'s long-lived OAuth
token.

```bash
heliox tool facebook-pages [--account <key>] -- <resource> <verb> [flags...]
```

Resources: `pages`, `page`, `post`, `comment`, plus top-level `insights`. Run
`-- <resource> --help` for the full flag surface.

## The mental model (one user, many Pages, one required `--page`)

The connection is a **Facebook user**, not a Page, and a user commonly admins
several Pages. So **always discover first**, then target one Page on every
other command:

```bash
heliox tool facebook-pages -- pages list          # the Pages you manage: id, name, category, tasks
heliox tool facebook-pages -- page get --page <page-id>
```

`--page <page-id>` is **required on every command except `pages list`**. Pick
the id from `pages list`; the `tasks` array tells you what you can do on each
Page (`CREATE_CONTENT` to publish, `MODERATE_CONTENT` to moderate comments,
`MANAGE`, `ANALYZE`).

You never see or handle a Page access token. The tool resolves the per-Page
token behind `--page` for you and uses it for the call; tokens never appear in
output. Reason in Page **ids**, not tokens.

## Reading

```bash
heliox tool facebook-pages -- post list --page <page-id> [--limit N] [--after <cursor>]
heliox tool facebook-pages -- post get  --page <page-id> <post-id>
heliox tool facebook-pages -- comment list --page <page-id> <post-id>
```

Paginate `post list` by passing the previous page's `paging.cursors.after` as
`--after`.

## Writing (publish + edit + delete)

```bash
heliox tool facebook-pages -- post create --page <page-id> --message "..." [--link https://...]
heliox tool facebook-pages -- post update --page <page-id> <post-id> --message "..."
heliox tool facebook-pages -- post delete --page <page-id> <post-id>
```

`post create` needs at least one of `--message` / `--link` and returns the new
post id (`{"id":"..."}`). Only text + link publishing is supported: photo,
video, scheduled, and Reel publishing are not (yet).

## Community management (comments)

```bash
heliox tool facebook-pages -- comment reply  --page <page-id> <comment-id> --message "..."
heliox tool facebook-pages -- comment hide   --page <page-id> <comment-id>            # hide spam
heliox tool facebook-pages -- comment hide   --page <page-id> <comment-id> --hidden=false   # unhide
heliox tool facebook-pages -- comment delete --page <page-id> <comment-id>
```

## Insights

```bash
heliox tool facebook-pages -- insights --page <page-id> \
  [--metrics page_impressions,page_post_engagements,page_fans] \
  [--period day|week|days_28] [--since <unix>] [--until <unix>]
```

Defaults to impressions / engagement / fans over the `day` period when
`--metrics` / `--period` are omitted.

## Footguns

- **`--page` is required** on everything except `pages list`. A missing `--page`
  is a usage error (exit 2), not a silent default.
- **Publishing needs the Page, not the user, and the right task.** The tool
  derives the Page token automatically, but the connected user must hold
  `CREATE_CONTENT` on that Page (from `pages list` `tasks`) or the publish
  fails with an "insufficient Page permission" error: reconnect won't fix it;
  the Page role must be granted on Facebook.
- **"Reconnect needed" vs "insufficient permission" are different.** An expired
  or revoked token surfaces as a reconnect-required error (re-run
  `heliox tool facebook-pages auth`). An insufficient-permission error means the
  token is fine but the Page grant/scope is not: do NOT reconnect blindly.
- **A failed Page lookup is reported distinctly** ("resolve Page access token
  for <page-id>: …") so you can tell "wrong Page id / no access to that Page"
  from "the post/read itself failed".
- **~60-day token.** The stored Facebook user token is long-lived (~60 days)
  with no refresh grant; once it lapses the connection must re-consent.
