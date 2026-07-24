# BoldSign (`heliox tool boldsign -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. BoldSign is a
**flat provider** (not grouped like `google`): everything after `--` is the
boldsign tool's own CLI.

```bash
heliox tool boldsign [--account <key>] -- <resource> <verb> [flags...]
```

BoldSign is e-signature: send a contract for signature (from a file or a
reusable template), track where a request stands, chase pending signers, cancel
a request, and pull the signed PDF plus its audit trail. Two resource groups:
`document` and `template`.

## Send is asynchronous (read this first)

`document send` returns a `documentId` **before** the document has finished
processing. A non-empty `documentId` means the request was accepted, not that
signers have been emailed yet. Do not assume completion from the send response;
poll `document get --id <documentId>` (or `document list`) to see the real
status.

Sending files with signers but **no fields, text tags, or auto-detect** is
rejected by BoldSign — the signer would have nowhere to sign. Pass one of
`--auto-detect-fields` (BoldSign finds signature fields) or `--text-tags`
(you embedded BoldSign text tags in the document), or send from a template
whose roles already carry fields.

## Documents

```bash
# Send local files for signature (files are base64-encoded into the request)
heliox tool boldsign -- document send \
  --file ./contract.pdf --title "MSA" \
  --signer "Alice <alice@example.com>" --signer "Bob <bob@example.com>" \
  --auto-detect-fields --json

# Or send by public file URL, with sequential signing and an expiry
heliox tool boldsign -- document send \
  --file-url https://example.com/nda.pdf --title "NDA" \
  --signer "Alice <alice@example.com>" --signer "Bob <bob@example.com>" \
  --signing-order --expiry-days 14 --text-tags --json

# List / monitor requests (page is 1-based; status/transmit-type filter)
heliox tool boldsign -- document list --page 1 --status WaitingForOthers \
  --status Completed --search "acme" --transmit-type Sent --json

# Status detail per signer
heliox tool boldsign -- document get --id <documentId> --json

# Download the (signed) PDF and the audit trail to local files
heliox tool boldsign -- document download  --id <documentId> --out ./signed.pdf
heliox tool boldsign -- document audit-log --id <documentId> --out ./audit.pdf

# Nudge pending signers (optionally only specific emails)
heliox tool boldsign -- document remind --id <documentId> \
  --email alice@example.com --message "gentle reminder" --json

# Cancel a request — a reason is required
heliox tool boldsign -- document revoke --id <documentId> --message "superseded by v2" --json
```

Flags for `document send`: `--file` / `--file-url` (repeatable; at least one
required), `--title` (required), `--message`, `--signer "Name <email>"`
(repeatable; at least one), `--signer-type Signer|Reviewer|InPersonSigner`
(default `Signer`), `--signing-order`, `--expiry-days N`,
`--auto-detect-fields`, `--text-tags`, `--disable-emails`, `--on-behalf-of`.

## Templates (the common recurring flow)

A template is a reusable document with predefined roles. Discover its roles,
then bind a signer to each `roleIndex`.

```bash
# Find templates and inspect a template's roles before sending
heliox tool boldsign -- template list --page 1 --search "nda" --json
heliox tool boldsign -- template get --id <templateId> --json

# Send from a template: bind "<roleIndex>:Name <email>" per role (index 1..50)
heliox tool boldsign -- template send --id <templateId> --title "Signed NDA" \
  --role "1:Alice <alice@example.com>" --role "2:Bob <bob@example.com>" \
  --field companyName=Acme --signing-order --json
```

`--role` is repeatable and required (at least one); `--field "<fieldId>=<value>"`
is repeatable and prefills existing template form fields.

## Output & exit codes

JSON-returning commands print the provider JSON on stdout verbatim.
`remind`/`revoke` return no body, so they print a small receipt
(`{"ok":true,"documentId":"…","action":"remind|revoke"}`); `download`/
`audit-log` write bytes to `--out` and print `{"ok":true,"path":"…","bytes":N}`.
Exit code `0` = success, `2` = a usage error (bad flags/inputs), `1` = a
BoldSign API/transport error. Add `--json` for a structured error envelope on
stderr.
