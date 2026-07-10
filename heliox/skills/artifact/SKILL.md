---
name: artifact
description: "Use `heliox artifact ...` to publish a self-contained HTML page (or a markdown file) as a durable, org-gated Helio artifact and hand a human a live link that stays the same as you update it: publish (or republish) a file, restore an old version, list the org's artifacts, or delete one. Reach for it when the deliverable is a page a person will open and keep open — a report, dashboard, analysis, or interactive prototype — especially one you'll refresh over time, or on a schedule from an automation. Every artifact names the human it's for (`--owner`). Not a downloadable file (that's an attachment) and not a collaborative document (that's `heliox:document`)."
user-invocable: false
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox artifact --help"
---

# Heliox Artifact

Start by reading `../shared/SKILL.md`.

`heliox artifact` publishes a **self-contained HTML page** — or a **markdown
file**, rendered server-side into a clean, styled page — as a first-class,
org-gated Helio resource. You get back a durable `view_url` at
`https://app.helio.im/a/<id>` that any signed-in member of the org can open, and
nobody outside it. Use it to hand a human a *live page* — a report, a dashboard,
an interactive prototype — instead of a dead screenshot or a download.

This is the right surface when the deliverable is rendered content meant to be
*viewed*. It is not the documents plane (`heliox:document` is collaborative
Tiptap prose you edit in place) and not an attachment (a downloadable file you
send with `-a`). Artifacts are published renders: you publish a new version and
the link stays the same.

## Publish

```bash
heliox artifact publish page.html --owner @alice
heliox artifact publish report.md --owner @alice
```

Publishing a file creates a new artifact and prints its `view_url` and id.
Share the `view_url` in conversation in your own words — publishing does not
announce anything on its own.

- **`--owner @<handle>`** (required when creating) names the human this
  artifact is *for* — usually whoever asked for it (take the handle from the
  message's `from` block; in a group, name the person it serves). It is set at
  create and can't change on republish, so you don't pass `--owner` when
  adding a version. The artifact isn't "yours" — it belongs to a person.
- **HTML** publishes as-is (see the content contract below).
- **Markdown** (`.md` / `.markdown`) is rendered server-side into a styled,
  readable page — publish the markdown file directly; do not convert it to
  HTML yourself. Keep the real file extension: the server keys rendering off
  the filename.
- **Title**: for HTML it comes from the page's own `<title>` element; for
  markdown, from the first heading. `--title` only overrides. A page with no
  title source and no `--title` is an explicit error, not a silent
  "Untitled".
- **`--favicon "📊"`** sets the browser-tab emoji for the artifact's page.
  Omitted → the existing favicon is kept.
- **Size cap**: 16 MiB per publish (the uploaded file, and for markdown also
  its rendered page).

## Republish (same link, live refresh)

```bash
heliox artifact publish page.html --artifact <id-or-view-url>
```

Pass `--artifact` to publish a new version of an existing artifact — it accepts
either the raw artifact id or the full `view_url` (paste the link back). The
`view_url` is unchanged, so iteration does not scatter links — and **any browser
tab already showing the artifact refreshes in place within seconds**, so a human
watching the page sees your update land live. Republishing the identical bytes
is a no-op (idempotent by content hash) — safe to retry after a timeout.

**Living reports (with an automation).** The strongest use of republish is a
recurring `heliox automation` that refreshes a report on a schedule: each run
republishes to the *same* artifact id, so the human keeps one permanent link
that updates itself. Anchor every run to the existing id (`--artifact <id>`);
do **not** mint a new artifact each run or the link churns. Find-or-create so
the automation is safe to re-run: `heliox artifact list --json` to locate the
existing one by title, else create it once (with `--owner`). Republishing
unchanged bytes is a no-op, so a scheduled run that finds nothing new costs
nothing.

## Version history & restore

The last 20 versions are retained. To bring an old version back:

```bash
heliox artifact restore --artifact <id-or-view-url> --to 3
```

Restore fetches version 3's content and republishes it as a **new** version —
history is append-only, the link is unchanged, and open tabs refresh to the
restored content. A version outside the retained window is an explicit
not-found error.

## List

```bash
heliox artifact list --json
```

Lists the org's live artifacts (id, title, latest version) — no page content.

## Delete

```bash
heliox artifact delete <id>
```

Soft-deletes an artifact so the link stops resolving. Deletion is sensitive (the
shared safety rule): only delete when the user asked for it.

## The content contract (what makes a valid HTML artifact)

The page is rendered in a sandboxed iframe that runs it as an opaque origin with
**no network access**. Author to these rules:

- **One fully self-contained HTML file.** Every asset — CSS, JS, images, fonts —
  inlined into that single file; images and fonts as `data:` URIs.
- **No external requests of any kind.** CDN scripts, external stylesheets, remote
  fonts, `fetch`/`XHR`/WebSocket calls are all blocked by the viewer's CSP. If
  the page needs a library, inline it.
- **No `localStorage`, no cookies.** The opaque origin has no persistent storage —
  artifacts are stateless. Hold state in memory for the life of the page.
- **Links may open new tabs.** In-page navigation to an external URL opens a new
  tab; that is allowed.

This contract is proven expressive enough for reports, dashboards, and
interactive prototypes. For prose deliverables you do not need to author HTML at
all — publish the markdown file and the server renders it into a page that
satisfies this contract.

Before authoring an HTML page by hand, read `references/design.md` in this
skill's directory — the design craft (treatment calibration, typography,
palette, the Helio theme model, layout, size budget). A published artifact
carries your name in front of the whole org; make it look deliberate.

## Shell-safe free-text flags

You almost never pass `--title` (the page's own title is the source of truth),
and `--favicon` is a single emoji. If a free-text flag value — a `--title` you
must set because the page has no title source, or a `--favicon` — carries any
shell-sensitive characters, do not put it on the command line. Follow the
shared rule: write the whole argument vector as a JSON array to a file with
your file tool, then run `heliox --args-file <path>` with nothing else on the
command line.

## Org-private artifact vs public throwaway demo

Org-private page → `heliox artifact publish`. Public throwaway demo of a runnable
app → the `cloudflare` plugin's `wrangler deploy --temporary`: the URL is on the
**public internet**, lives **60 minutes** unless the human opens the **claim
URL** and keeps it under their own Cloudflare account — always hand them that
URL. **Never put org-private data in a temporary deploy; use an artifact.**

## Safety

- Publishing makes the page viewable by every member of the org — do not publish
  content that should stay in a private channel.
- The link is durable and lands in chat history; republish to the same id rather
  than churning new links — viewers refresh in place.
- Delete is sensitive; confirm intent unless already asked.
