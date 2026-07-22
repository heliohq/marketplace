# Google Drive (`heliox tool google drive -- ...`)

Read [google.md](./google.md) first for auth and account selection. Everything
after `--` is the drive tool's own CLI. Connecting Gmail (or any other Google
app) does **not** connect Drive — each Google app is its own connection with its
own consent. If a Drive command reports no connection, run
`heliox tool google auth drive` and forward the link to the user.

## What this tool can see: read this first

Drive here runs on the **`drive.file`** scope. It only sees files it created or
that the user explicitly shared with it — **not the user's whole Drive**. Think
of it as Helio's **delivery surface**, not a "search my Drive" assistant:

- You can upload deliverables, organize them in folders you make, export
  Workspace docs, and share them out.
- You **cannot** find a user's pre-existing files. "Find that contract in my
  Drive" will not work — `files list` and `files get` on files this tool never
  touched return nothing / a 404.

When the user asks for an existing file you did not create, **explain the
boundary and ask them to share it into Drive with you (or paste the content /
link)** — do **not** retry, reword the `--query`, or hunt. A 404 on such a file
is the scope working as designed, not a transient error.

## Core commands

```bash
# Account + storage self-check
heliox tool google drive -- about --json

# List files THIS TOOL can see (native Drive query syntax via --query)
heliox tool google drive -- files list --query "name contains 'report' and mimeType='application/pdf'" --json
heliox tool google drive -- files list --parent <folderId> --json
heliox tool google drive -- files list --query "modifiedTime > '2026-01-01T00:00:00'" --json

# Metadata + the delivery link (webViewLink) for a file
heliox tool google drive -- files get <id> --json

# Deliver a result: upload, then hand back the webViewLink
heliox tool google drive -- files upload ./report.pdf --parent <folderId> --json
heliox tool google drive -- files upload ./data.csv --convert --json   # → a Google Sheet

# Organize (reversible, no confirmation needed — private domain)
heliox tool google drive -- files mkdir "Q3 Deliverables" --parent <folderId>
heliox tool google drive -- files update <id> --name "final.pdf" --parent <destFolder> --remove-parent <srcFolder>
heliox tool google drive -- files copy <id> --name "backup.pdf"
heliox tool google drive -- files trash <id>...      # recoverable; the ONLY delete this tool has

# Get content out
heliox tool google drive -- files download <id> --save ./out/          # binary/blob files
heliox tool google drive -- files export <id> --format pdf --save ./out/  # Docs/Sheets/Slides → pdf|docx|xlsx|pptx|csv|txt

# See / manage who a file is shared with
heliox tool google drive -- permissions list <file-id> --json
```

Check `-- --help` rather than guessing flags. `--query` is Drive's native `q`
syntax — pass it through verbatim (`'<folderId>' in parents`,
`name contains 'x'`, `mimeType='application/vnd.google-apps.document'`,
`trashed = false`).

## Sharing goes through the approval gate

Uploading and organizing stay in your private domain — do them freely.
**Sharing is the one place data leaves that domain**, and the gate enforces
the check: `files share` (to a person or `--anyone`) and `permissions update`
are policy-gated — instead of running, heliox exits with `APPROVAL_REQUIRED`
and prints the exact request/replay commands (full flow in the tool skill's
"Approval gate" section). Put **what file, to whom, and what role** (reader /
commenter / writer) in the request `--message` — and for `--anyone`
(link-visible to anyone with the link, the highest-exposure form) say that
public-exposure fact explicitly. The approval card **is** the human check —
do not also pre-confirm in chat.

```bash
heliox tool google drive -- files share <id> --with alice@example.com --role reader --message "Here's the report"
heliox tool google drive -- files share <id> --anyone --role reader
```

**Narrowing is yours to do directly**: lowering a role (writer → reader) or
`permissions delete <file-id> <perm-id>` (revoking a share) shrinks exposure
and is not gated — no confirmation needed.

## Working with Gmail: files move via the filesystem

There is no cross-tool API bridge. To move a Gmail attachment into Drive, or a
Drive file into an email, go through local files:

```bash
# Gmail attachment → Drive
heliox tool google gmail -- messages attachments <msg-id> --save ./tmp/
heliox tool google drive -- files upload ./tmp/<file> --json

# Drive file → Gmail attachment
heliox tool google drive -- files export <id> --format pdf --save ./tmp/
heliox tool google gmail -- messages send --to a@b.com --subject "..." --body-file ./m.md --attach ./tmp/<file>.pdf
```

## Failure notes

- **404 on `files get` / `download` / `export`** = the file is outside this
  tool's authorization domain (not created here, not shared with it). Explain
  the `drive.file` boundary to the user; do not retry.
- **`export` is capped at 10MB** by the Drive API. If it fails on size, use
  `files download` (for a blob file) or suggest splitting — do not silently
  fall back.
- **Delete is `trash` only** (recoverable). There is no permanent delete — say
  so if the user asks to "delete forever."
- **403 with a scope hint** = the connection predates the needed scope; ask the
  user to reconnect (`prompt=consent` re-grants everything).
