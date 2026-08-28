# Dropbox Sign (`heliox tool dropbox-sign -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Dropbox Sign
(formerly HelloSign) is a **flat provider** (not grouped like `google`):
everything after `--` is the dropbox-sign tool's own CLI.

```bash
heliox tool dropbox-sign [--account <key>] -- <resource> <verb> [flags...]
```

Dropbox Sign is an e-signature service. Your real job is the **send → track →
download** loop: send a document out for signature, watch whether it's signed,
chase signers, and pull the completed signed PDF back, plus reuse of saved
templates. Commands hang under three resource groups: `signature-request`,
`template`, and `account`. Every command supports `--json`.

> Not to be confused with **Dropbox** the file-storage product, which is not
> a Helio tool: separate product and account. This tool signs documents; it
> does not browse Dropbox files.

## Core commands

### Send a document for signature

```bash
# from a public URL (simplest when you already have a link)
heliox tool dropbox-sign -- signature-request send \
  --file-url https://example.com/nda.pdf \
  --signer "Alice Smith:alice@example.com" \
  --signer "Bob Lee:bob@example.com" \
  --title "Mutual NDA" --subject "Please sign" --json

# from a local file upload (repeatable; use --file OR --file-url, never both)
heliox tool dropbox-sign -- signature-request send \
  --file /path/to/contract.pdf \
  --signer "Carol Ng:carol@example.com" --json

# from a saved template (roles must match the template's signer roles)
heliox tool dropbox-sign -- signature-request send-with-template \
  --template <template_id> \
  --signer "Client:Dana Fox:dana@example.com" --json
```

- `--signer` is repeatable; **flag order sets the signing order** for `send`.
- Format is `"Name:email"` for `send`, `"Role:Name:email"` for
  `send-with-template` (the email is always after the last colon).
- `--cc <email>` (repeatable), `--title`, `--subject`, `--message` are optional.
- **`--test-mode`** creates a non-legally-binding, watermarked request that does
  **not** consume signature quota or require a paid plan. Use it for any dry run.

### Track and chase

```bash
heliox tool dropbox-sign -- signature-request list --page 1 --page-size 20 --json
heliox tool dropbox-sign -- signature-request get <signature_request_id> --json
heliox tool dropbox-sign -- signature-request remind <signature_request_id> --email alice@example.com --json
heliox tool dropbox-sign -- signature-request cancel <signature_request_id> --json
```

`get` returns per-signer state (`signatures[]` with `status_code` / `signed_at`)
plus `is_complete` / `is_declined`.

### Download the signed document

```bash
# stream bytes to a file (a JSON receipt goes to stdout)
heliox tool dropbox-sign -- signature-request files <signature_request_id> --file-type pdf --out /tmp/signed.pdf
# or stream raw bytes to stdout (omit --out)
heliox tool dropbox-sign -- signature-request files <signature_request_id> --file-type zip
```

### Templates and account

```bash
heliox tool dropbox-sign -- template list --page-size 20 --json
heliox tool dropbox-sign -- template get <template_id> --json     # roles + fields
heliox tool dropbox-sign -- account get --json                    # identity + quota
```

Run `-- <resource> <verb> --help` for the exact flags rather than guessing.

## Footguns (where agents go wrong)

- **Provide exactly one document source.** `send` requires `--file` **or**
  `--file-url`, never both and never neither: otherwise it's a usage error
  (exit 2) before any API call.
- **`list` is scoped to this connection.** It reflects requests created *through
  this connected account*, not the user's entire Dropbox Sign history. Don't
  describe it as whole-account history.
- **Prefer `--test-mode` for dry runs.** Real (non-test) sends need a paid
  Dropbox Sign plan on the connected account; without one the API returns 402.
  `--test-mode` avoids both quota spend and the paid-plan requirement.
- **Roles matter for templates.** `send-with-template` signers are
  `"Role:Name:email"`; the role must match a signer role defined on the
  template, or the send is rejected.
- **`--account` when more than one Dropbox Sign account is connected.** A `409`
  lists the candidate account keys; re-run with `--account <key>` (before `--`).

## Safety

- Sending a signature request emails real people and can create a **legally
  binding** document. Follow the sensitive-operation rule in
  [../SKILL.md](../SKILL.md): confirm the recipients, document, and intent with
  the user before a non-test send, and prefer `--test-mode` until they approve.
- `cancel` cannot be undone; confirm the request id before cancelling.
