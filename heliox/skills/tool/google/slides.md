# Google Slides (`heliox tool google slides -- ...`)

Read [google.md](./google.md) for auth and account selection. Everything after
`--` is the slides tool's own CLI. This connection covers **Google Slides
presentations only**: it reads and edits any deck you have a link to, but it
cannot search Drive, copy or export decks, or change sharing (see
[What this connection cannot do](#what-this-connection-cannot-do)).

## Links are ids

Every `<presentation-id-or-url>` argument accepts the full Slides URL the user
pastes (`https://docs.google.com/presentation/d/<id>/edit`). The tool extracts
the id. Never ask the user to hand-extract an id.

## Read before you write

Slide and element object ids are the currency of every edit, and you cannot
guess them:

```bash
# Deck outline: per slide, its object id + layout + text + speaker notes
heliox tool google slides -- presentations get <pid-or-url>
heliox tool google slides -- presentations get <pid-or-url> --slide 2      # one slide (1-based index or slide id)
heliox tool google slides -- presentations get <pid-or-url> --json         # raw Presentation JSON (large)

# Locate an element's object id inside one slide before editing it
heliox tool google slides -- pages get <pid-or-url> <slide-id>
```

Blind-writing an object id you did not read from `presentations get` /
`pages get` will fail.

## Create and edit (net-new / reversible: no confirmation needed)

This layer only adds information or reorders; nothing existing is overwritten.

```bash
# New deck -> prints presentationId + editor URL
heliox tool google slides -- presentations create --title "Q3 Review"

# Add a slide; --title/--body fill the layout's TITLE/BODY placeholders atomically.
# --layout is a PredefinedLayout: BLANK, TITLE, TITLE_AND_BODY, SECTION_HEADER, ...
heliox tool google slides -- slides add <pid> --layout TITLE_AND_BODY --title "Agenda" --body "First\nSecond"
heliox tool google slides -- slides add <pid> --layout BLANK --at 0        # 0-based position

# Duplicate / reorder (reversible)
heliox tool google slides -- slides duplicate <pid> <slide-id> --at 3
heliox tool google slides -- slides move <pid> <slide-id>... --to 0

# Add text into an existing text element (default at start; --at index or --append)
heliox tool google slides -- text insert <pid> --object <element-id> --text "note" --append

# Insert an image from a PUBLIC https URL (Google fetches it: <=50MB, <=25MP, PNG/JPEG/GIF)
heliox tool google slides -- images insert <pid> --slide <slide-id> --url https://example.com/chart.png --at 100,50 --size 400x300
```

## Overwrite / delete (highest risk: confirm first)

The API has **no undo**. The only recovery is the user's own Slides UI version
history (File → Version history). For any deck the **assistant did not create**,
before you overwrite or delete:

1. Run `presentations get` and report to the user exactly what will change.
2. Get the user's confirmation for that specific change.
3. After editing, render a `pages thumbnail` and show it so they can verify.

```bash
# Template fill: the right path for {{placeholder}} decks. --slide limits scope.
heliox tool google slides -- text replace <pid> --find '{{name}}' --replace 'Ada' --match-case --slide <slide-id>

heliox tool google slides -- text delete <pid> --object <element-id> --range 2:5   # empty range = all text
heliox tool google slides -- slides delete <pid> <slide-id>...                     # whole slides
heliox tool google slides -- elements delete <pid> <element-id>...                 # elements inside a slide
```

Template filling: prefer one `text replace` per placeholder (or batch several
into one `batch-update`) over hand-writing `text insert` calls.

## Visual verification

`contentUrl` from getThumbnail is short-lived and billed as an expensive read,
so the tool downloads the PNG to your working directory instead of echoing a
URL. Show it to the user after edits.

```bash
heliox tool google slides -- pages thumbnail <pid> <slide-id> --save ./out/ --size LARGE   # LARGE|MEDIUM|SMALL
```

## Escape hatch: `batch-update`

The synthetic verbs above cover the high-frequency edits. For anything else
(tables, shapes, lines, groups, transforms, z-order), pass raw batchUpdate
requests through verbatim. `--requests` accepts a Request array, a single
Request object, or a full `{"requests":[...]}` body.

```bash
heliox tool google slides -- batch-update <pid> --requests '[{"createShape":{"objectId":"box1","shapeType":"TEXT_BOX","elementProperties":{"pageObjectId":"slide1","size":{"width":{"magnitude":300,"unit":"PT"},"height":{"magnitude":60,"unit":"PT"}},"transform":{"scaleX":1,"scaleY":1,"translateX":50,"translateY":50,"unit":"PT"}}}}]'
```

**The whole batch is atomic**: if any request is invalid, none are applied and
the error names the failing `requests[N]`. Fix that request and resend.

## What this connection cannot do

Do not promise these: the `presentations` scope does not cover them. Give the
alternative instead:

- **Search / list decks by name** ("find my Q3 deck"): needs Drive. Ask the
  user for the link.
- **Copy an entire deck** ("duplicate this template"): needs Drive. Rebuild
  net-new, or have the user copy it in Slides and paste the new link.
- **Export to PDF / PPTX**: needs Drive. `pages thumbnail` per slide is the
  low-fidelity stand-in.
- **Change sharing / permissions**: needs Drive.
- **Embed a live Sheets-linked chart / refresh chart data**: the
  `createSheetsChart` / `replaceAllShapesWithSheetsChart` / `refreshSheetsChart`
  requests require a Sheets scope this connection does not carry; calling them
  via `batch-update` returns 403. Generate the chart as an image in the runtime
  and use `images insert --url` instead.
- **Insert a local (non-public) image file**: `createImage` needs a public
  URL; there is no Drive upload surface in v1.

## Failure notes

- **Not connected / auth error** → guide the user to
  `heliox tool google auth slides`.
- **Multiple accounts, none chosen (409)** → pass `--account <key>` before `--`.
- **404** → the deck id is wrong or not visible to the connected account.
  Re-check the link and the `--account`.
- **403 with a scope hint** → the connection predates the needed scope, or you
  called a Sheets-linked-chart request; reconnect for the former, use the image
  path for the latter.
