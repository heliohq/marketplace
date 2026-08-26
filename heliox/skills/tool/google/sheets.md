# Google Sheets (`heliox tool google sheets -- ...`)

Read [google.md](./google.md) for auth and account selection. Everything after
`--` is the sheets tool's own CLI. Every `<id>` argument accepts either the bare
spreadsheetId or a full link (`https://docs.google.com/spreadsheets/d/<id>/edit#gid=0`).
The tool extracts the id, so paste whatever the user gave you.

## Work by ID: there is no list/search

The Sheets API has **no "list my spreadsheets"** (that is Drive, which this tool
does not reach). You find a spreadsheet only from a link/ID the user gives you,
or from one you just created. On any new spreadsheet the **first step is always
`spreadsheets get`**. It returns the title and the tab list (name, gid, grid
size). Never guess tab names.

```bash
heliox tool google sheets -- spreadsheets get <id> --json   # title + tabs (title/gid/rows×cols), no cell data
```

## Core loop: read → write / append

```bash
# Read one or more A1 ranges (multiple --range → one batchGet call)
heliox tool google sheets -- values get <id> --range "'Q3 Budget'!A1:D20" --json
heliox tool google sheets -- values get <id> --range Sheet1!A:A --range Sheet1!C:C --json
heliox tool google sheets -- values get <id> --range A1:D1 --render formula        # or --render unformatted

# Append rows: the FIRST CHOICE for logging / incremental records (does not overwrite)
heliox tool google sheets -- values append <id> --range Log!A1 --values-json '[["2026-07-16","done",42]]'

# Overwrite a range (see "write before read" below)
heliox tool google sheets -- values update <id> --range Sheet1!A1 --csv-file ./rows.csv
heliox tool google sheets -- values clear  <id> --range Sheet1!A2:D999
```

Values are a **row-major 2D array**: `--values-json '[["r1c1","r1c2"],["r2c1","r2c2"]]'`,
or `--csv-file <path>` to load a CSV grid.

## Create and manage tabs

```bash
heliox tool google sheets -- spreadsheets create --title "2026 Plan" --tab Jan --tab Feb --json  # returns id + URL to forward
heliox tool google sheets -- tabs add     <id> --title Notes
heliox tool google sheets -- tabs rename  <id> --tab Sheet1 --title Data
heliox tool google sheets -- tabs duplicate <id> --tab Data --title "Data backup"
heliox tool google sheets -- tabs copy-to <id> --tab Data --dest <other-spreadsheet-id>
heliox tool google sheets -- tabs delete  <id> --tab Data        # irreversible. Confirm first (see below)
```

`--tab` takes either the tab **title** or its numeric **gid** (from the URL's
`#gid=` or `spreadsheets get`). If two tabs share a title, the tool asks for the
gid.

For anything the safe verbs don't cover (formatting, conditional formatting,
sorting, freezing rows, charts, pivot tables), use the raw escape hatch. It
passes a Sheets API `batchUpdate` body straight through (an array of requests or
a full `{"requests":[...]}` object):

```bash
heliox tool google sheets -- spreadsheets batch-update <id> --request-file ./requests.json
```

## Soft guardrail: write before read, confirm destructive edits

The API has **no undo**. Sheets keeps a Drive version history the user can roll
back to in the UI, but that saves *data*, not *structure*: a deleted tab breaks
every cross-tab formula that referenced it (they turn into `#REF!`).

- **Before any `update` or `clear`**: first `values get` the target range and
  report the scale ("this will overwrite N rows × M columns of existing data")
  and get the user's OK. For incremental records, prefer `append` over `update`
  so you never step on existing rows.
- **Before `tabs delete`, a large `clear`, or a `batch-update` containing any
  `deleteSheet` / `deleteDimension` / `deleteRange` request**: confirm with the
  user first. These are the irreversible, structure-breaking operations.

## The USER_ENTERED trap

Writes default to `USER_ENTERED`: values are parsed like someone typed them
into the UI. `=SUM(A1:A3)` becomes a formula; `1/2` becomes a date; a leading
`+` or `0` may be stripped. When writing **literal user text** (phone numbers,
IDs, part numbers, anything starting with `=`, `+`, or `-`), pass `--raw` so it
is stored verbatim. Otherwise the data silently changes shape.

## Reading large tables

- `values get` trims trailing empty rows/columns from its response. To learn
  "how many rows of data exist", read the returned array length (or probe one
  column like `--range Sheet1!A:A`), **not** the grid size.
- The `rowCount`/`columnCount` from `spreadsheets get` is the allocated grid
  **capacity** (a new sheet defaults to 1000 rows), not the data row count. Use
  it only as an upper bound for chunked reads.
- For a huge sheet, read in ranges. Don't dump the whole grid in one call.

## A1 quoting

When a tab title contains a space or non-ASCII characters, wrap it in single
quotes inside the range: `'Q3 预算'!A1:D10`. `Sheet1!B:B` is a whole column;
`Sheet1!A1:D` is columns A-D from row 1 down.

## Failure notes

- **403 / 404 on a spreadsheet is usually a sharing problem, not a scope
  problem.** The `spreadsheets` scope decides whether the tool may call the API
  at all; whether *this Google account* can open *that file* is Drive-side ACL.
  Ask the user to have the file's owner share it with the connected account (or
  confirm the link). Do **not** tell them to reconnect.
- **403 with a scope hint** (an older connection made before this scope existed)
  → that one *is* a reconnect: disconnect and reconnect to re-grant.
- **429 quota** → the tool backs off and retries once. Batch reads/clears with
  multiple `--range` (one call); for bulk writes, merge into a single large
  `update` range or use `append`. Never loop cell-by-cell.

Check `-- --help` (or `<group> --help`) rather than guessing flags.
