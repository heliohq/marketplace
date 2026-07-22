# OneDrive (`heliox tool microsoft onedrive -- ...`)

Read [microsoft.md](./microsoft.md) for auth and account selection. Everything
after `--` is the OneDrive tool's own CLI, a faithful projection of Microsoft
Graph `/me/drive`. Address items by id or by path with `--path
/folder/file.ext`; search passes Graph drive search through `--query '<text>'`.
Scope is the user's **own** OneDrive only (not shared libraries / SharePoint).

## Core commands

```bash
# Browse / read
heliox tool microsoft onedrive -- items list --path /Documents --max 50 --json    # children of a folder
heliox tool microsoft onedrive -- items get --path /Documents/report.docx --json  # metadata: name, size, mimeType, lastModified
heliox tool microsoft onedrive -- search --query 'quarterly' --max 20 --json

# Download (lands in your working directory; then use normal file/attachment flows)
heliox tool microsoft onedrive -- download --path /Documents/report.docx --save ./work/

# Upload / organize (reversible)
heliox tool microsoft onedrive -- upload ./out/report.pdf --to /Documents        # small direct / large chunked, chosen internally
heliox tool microsoft onedrive -- items mkdir --name "Reports" --path /Documents
heliox tool microsoft onedrive -- items move <id> --to <dir-id> --name new.pdf
heliox tool microsoft onedrive -- items rename <id> --name final.pdf

# Outward / not-routine
heliox tool microsoft onedrive -- items share <id> --type view --scope organization   # create a sharing link
heliox tool microsoft onedrive -- items delete <id>...                                # to recycle bin
```

Check `-- --help` for full flags. Every command takes `--json`; lists default
to a human-readable table with `--page <token>` for explicit pagination.

## Sharing and deleting

- **Public links go through the approval gate.** `items share --scope
  anonymous` (anyone with the link) is policy-gated — instead of running,
  heliox exits with `APPROVAL_REQUIRED` and prints the exact request/replay
  commands (full flow in the tool skill's "Approval gate" section); say the
  public-exposure fact explicitly in the request `--message`. The approval
  card **is** the human check — do not also pre-confirm in chat. Default to
  `--scope organization`, which stays inside the org and is routine — not
  gated, no confirmation needed.
- **Confirm before delete**, even though items go to the recycle bin — surprising
  deletions erode trust. Report what will be deleted first.
- **Confirm before overwriting** an existing file on upload.

## Failure notes

- No connection → `heliox tool microsoft auth onedrive`, relay the link.
- 409 with account candidates → re-run with `--account <key>`.
- 403 scope hint / 401 reconnect required → disconnect and reconnect (fresh
  consent; `prompt=select_account` re-picks the account).
- Shared libraries / SharePoint sites are not accessible in v1 — only the user's
  own OneDrive. If the user points at a shared/team library, say it is out of
  scope rather than guessing a path.
- Permanent delete is intentionally not exposed; `items delete` goes to the
  recycle bin.
