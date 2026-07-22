# Notion (`heliox tool notion -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Notion is a
**flat provider** (not grouped like `google`): everything after `--` is the
notion tool's own CLI.

```bash
heliox tool notion [--account <key>] -- <resource> <verb> [flags...]
```

The tool is **markdown-native and MCP-aligned**: you read and write page
content as Markdown, not Notion block JSON. Two top-level verbs are
cross-resource (`fetch`, `search`); everything else hangs under a resource
group (`page`, `db`, `data-source`, `view`, `comment`, `user`, `task`).

## The mental model (read this first — it prevents the #1 footgun)

A Notion **page** has two separate halves, and they are read by different
commands:

- **Body** — the free-form Markdown area under the title. Read/written as
  markdown.
- **Properties** — for a **database row**, its column values (Status, Priority,
  Owner, dates…). These live in `properties`, **not** in the body.

`fetch <id>` switches output by id type: **page → Markdown body**, **database /
data-source → JSON**. So `fetch` on a database *row* returns only its body —
which is usually empty — and **will not show you the row's field values**. To
read a row's fields, query its data source. (See Footguns.)

## Core commands

### Read

```bash
# fetch auto-detects the id type: page→markdown, database/data-source→JSON
heliox tool notion -- fetch <id> --json
heliox tool notion -- fetch self --json          # workspace + current-user identity

# search across pages and data sources
heliox tool notion -- search --query "onboarding" --json

# query a data source (this is how you read database ROWS + their field values)
heliox tool notion -- db query <data-source-id> --filter '<json>' --sorts '<json>' --all --json
```

`fetch <db-url>`: a database view URL (`...?v=...`) resolves to the database;
its `data_sources[]` gives the `data-source-id` you feed to `db query`.

### Write page content (Markdown in, aliases for the common edits)

```bash
# create one or more pages; --pages is a JSON ARRAY (each item: parent + properties + content)
heliox tool notion -- page create --pages '[{"parent":{"page_id":"<id>"},"properties":{"title":{"title":[{"text":{"content":"Hello"}}]}},"content":"# Hi\n\nbody"}]' --json

# canonical update: --command replace_content | insert_content | update_content
heliox tool notion -- page update <page-id> --command replace_content --content "# New body" 

# ergonomic aliases (all route to page update):
heliox tool notion -- page replace <page-id> --new-str "# Full replacement"      # replace_content
heliox tool notion -- page append  <page-id> --content "appended line"           # insert_content @ end
heliox tool notion -- page insert  <page-id> --content "intro" --at start        # insert_content @ start|end
heliox tool notion -- page edit    <page-id> --old "typo" --new "fixed"          # update_content (repeatable --old/--new, zipped in order)

# move / duplicate
heliox tool notion -- page move --page-or-database-ids '["<id>"]' --new-parent <id|url|json>
heliox tool notion -- page duplicate <page-id> --json
```

- `--content`/`--new-str` accept Markdown inline; large single-segment content
  can come from `--file <path>`.
- Deleting existing child blocks during an update requires the global
  `--allow-deleting-content` flag (fail-safe: it will not silently drop blocks).

### Databases, data sources, views

```bash
heliox tool notion -- db create --parent <id|url> --title "Tracker" --properties '<schema-json>' --json
heliox tool notion -- data-source update <data-source-id> --name "Renamed DS"     # --name maps to rich-text title
heliox tool notion -- view create --database-id <id> --data-source-id <ds> --name "Board" --type board --json
heliox tool notion -- view update <view-id> --name "..." --filters '<json>' --sorts '<json>'
```

### Comments, users, async tasks

```bash
# comment: exactly one target (mutually exclusive), --content is Notion-flavored MARKDOWN
heliox tool notion -- comment create --page-id <id> --content "**bold** + [link](https://x)" --json
heliox tool notion -- comment create --block-id <id> --content "on this block" --json
heliox tool notion -- comment create --discussion-id <id> --content "reply in thread" --json
heliox tool notion -- comment list <page-id> --json     # NOTE: returns UNRESOLVED comments only

# users
heliox tool notion -- user get self --json         # /users/me
heliox tool notion -- user get <user-id> --json     # resolve a created_by/last_edited_by id
heliox tool notion -- user get --query "alice" --json

# async task status (manual fallback; --allow-async auto-polls this for you)
heliox tool notion -- task get <task-id> --json
```

Run `-- <resource> --help` (or `-- <resource> <verb> --help`) for the exact
flags rather than guessing.

## Footguns (the important part — these are where agents go wrong)

- **A database row's fields are NOT in `fetch`.** `fetch <row-id>` returns the
  row's *body* (usually empty) — its Status/Priority/Owner/etc. live in
  `properties`. Reading a record and seeing "empty" almost always means you
  used `fetch`; use **`db query <data-source-id>`** to get rows *with* their
  field values. The tool prints a stderr hint when a fetched body is empty and
  the page looks like a database row.
- **Do not wait for an async task that will never come.** Creating a page from
  a template (`page duplicate`, template create) returns the page **synchronously**
  and does not hand back a task handle. Only `--allow-async` *with markdown
  content* produces a task to poll. Don't loop on `task get` for a template
  create.
- **Callout syntax is `<callout>`, not GFM.** Notion Markdown uses
  `<callout icon="🎯" color="blue_bg">…</callout>`. GFM admonitions
  (`> [!NOTE]`) do **not** render as callouts.
- **Comments take Markdown, not plaintext** (via the endpoint's `markdown`
  field): inline bold/italic/strike/code/links, inline equations, and
  `@mention` work. `comment list` returns **unresolved comments only** — a
  resolved discussion won't appear.
- **`properties` must be REST value shape**, not shorthand: a title is
  `{"title":[{"text":{"content":"Hello"}}]}`, not `{"title":"Hello"}`. The CLI
  passes properties through verbatim.
- **`view create` needs `--data-source-id` and `--name` on every parent mode**
  (including `--create-database`) — a view without a data source is a `400`.
- **Moving a database ≠ moving a page.** `page move` routes by id type: a page
  id → move endpoint; a **database id → re-parent** (databases have no move
  endpoint); a data-source id is rejected (move the database that owns it).
- **There is no delete/archive command** — by design. The tool cannot remove
  pages, databases, or comments; clean up test artifacts in the Notion UI.
- **`--account` when more than one Notion account is connected.** A `409` lists
  the candidate account keys; re-run with `--account <key>` (before the `--`).

## Safety

- Comments and page edits are team-internal collaboration — routine, not
  approval-gated, and no pre-confirmation needed (see the tool skill's
  "Approval gate" section for what is gated).
- Content edits with `--allow-deleting-content` can drop existing blocks;
  confirm scope before running one against a page you didn't create.
