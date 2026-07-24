# PandaDoc (`heliox tool pandadoc -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. PandaDoc is a
**flat provider** (not grouped like `google`): everything after `--` is the
pandadoc tool's own CLI.

```bash
heliox tool pandadoc [--account <key>] -- <resource> <verb> [flags...]
```

PandaDoc is a document-workflow / eSignature product. Commands hang under a
resource group (`document`, `template`, `contact`) plus top-level `whoami` and
a raw `api` escape hatch. Default output is concise text (id / status / name);
add `--json` to any command for the provider's full JSON response.

## The core loop: send a document from a template for signature

```bash
# 1. Find a template and inspect its roles / tokens / fields BEFORE creating
heliox tool pandadoc -- template list --q "nda" --json
heliox tool pandadoc -- template details <template-id> --json   # roles + tokens + fields

# 2. Create a document from the template (see the async note below)
heliox tool pandadoc -- document create \
    --template <template-id> --name "NDA — Acme" \
    --recipient alice@acme.com:Client:Alice:Smith \
    --token Sender.Company=Helio \
    --field CustomerName=Alice \
    --json

# 3. Send it for signature
heliox tool pandadoc -- document send <document-id> --subject "Please sign" --message "..." 

# 4. Track status until completed
heliox tool pandadoc -- document status <document-id>            # one-line status
heliox tool pandadoc -- document details <document-id> --json    # recipients, fields, dates

# 5. Retrieve the signed PDF into the workspace
heliox tool pandadoc -- document download <document-id> --out ./nda-signed.pdf --protected
```

- `--recipient` is `email[:role[:first[:last]]]` (repeatable). Only the email is
  required; the role must match a role on the template. `first`/`last` override
  the contact record when given.
- `--token name=value` fills template variables (e.g. `Sender.Company`).
  `--field name=value` fills merge fields (wrapped as `{value: ...}` for you);
  signature fields cannot be pre-filled.
- `--metadata key=value` attaches searchable metadata.
- For a payload the flags can't express, pass the full create body with
  `--body '<json>'` or `--body-file <path>` (mutually exclusive with the
  structured flags).

## Footguns (where agents go wrong)

- **A freshly created document is not immediately sendable.** `POST /documents`
  returns `status: document.uploaded`; PandaDoc processes it in the background
  and only then flips it to `document.draft`. `document create` **waits for the
  draft flip for you** (polls up to ~60s) so a following `document send`
  succeeds — do not `send` right after a `--no-wait` create, and do not build
  your own poll loop. If the wait times out, the command prints the document id
  so you can resume with `document status <id>`.
- **`send` before draft is an error, not a retry.** If you used `--no-wait`,
  check `document status <id>` is `document.draft` before sending; sending an
  still-uploading document surfaces the provider error as-is.
- **`download` writes bytes to `--out`, it does not print the PDF.** Use
  `--protected` for the certified/completed copy (`download-protected`); plain
  `download` is the working copy. Under `--json` the command prints a receipt
  `{"path": ..., "bytes": N}`.
- **Contacts are optional convenience.** `contact list --email <addr>` filters by
  exact email; `contact create` reuses names/companies across sends. Recipients
  on `document create` do not require a pre-existing contact.
- **`--account` when more than one PandaDoc account is connected.** A `409`
  lists the candidate account keys; re-run with `--account <key>` before the `--`.

## Escape hatch

For endpoints without a first-class command (folders, content library, quotes,
etc.), use the raw passthrough — credentials are still injected:

```bash
heliox tool pandadoc -- api GET /documents --query count=5 --query status=document.sent
heliox tool pandadoc -- api POST /contacts --body '{"email":"z@z.com"}'
```

## Safety

- Sending a document emails real recipients and starts a legally-binding
  signature flow — follow the sensitive-operation rule in
  [../SKILL.md](../SKILL.md) and confirm recipients + template before `send`.
  Use `--silent` on `send` to create the sent state without emailing, when you
  only need the signing link (`document link <id> --recipient <email>`).
- `document delete` is destructive; only remove drafts you created.
