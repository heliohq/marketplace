# SignNow (`heliox tool signnow -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. SignNow is a
**flat provider** (not grouped): everything after `--` is the signnow tool's
own CLI. Use it to send documents out for e-signature, track who has signed,
nudge or recall pending signers, and pull down the executed PDF.

```bash
heliox tool signnow [--account <key>] -- <resource> <verb> [flags...]
```

Every command emits JSON. Resource groups: `document`, `invite`, `template`,
`link`; plus top-level `whoami`.

## The mental model (read this first)

The signature lifecycle is: **upload a document → add fillable fields (or
extract them from text tags) → invite signers → track invite status → download
the signed PDF**. A template is a reusable document you `copy` into a fresh
document per agreement.

`document list` is the "find the doc to act on" command, and it deliberately
merges **two** SignNow listing surfaces:

- freshly-uploaded documents you have not edited yet, and
- modified / in-flight documents (fields, texts, or signatures added).

A doc you just uploaded lives only in the first until its first edit, so the
merged, deduped list is the one you want. There is no need to call two
endpoints yourself.

## Core commands

### Find & inspect

```bash
heliox tool signnow -- whoami                       # authenticated account (id, primary_email)
heliox tool signnow -- document list --limit 20     # merged: fresh + in-flight, deduped by id
heliox tool signnow -- document get <document-id>   # roles, field invites + statuses, signature count
```

### Prepare a document

```bash
# upload a PDF/DOCX to start a flow (filename becomes the document name unless --name)
heliox tool signnow -- document upload --file ./nda.pdf --name "Q3 NDA"

# upload and auto-extract fillable fields from the document's text tags
heliox tool signnow -- document upload --file ./tagged.pdf --extract-fields

# add fillable fields explicitly (JSON array of field objects: x/y/page_number/type/role)
heliox tool signnow -- document add-fields <document-id> --fields '[{"x":10,"y":20,"page_number":0,"type":"signature","role":"Signer 1"}]'
```

### Send for signature

```bash
# role-based field invite: --to is a JSON array of {email, role, order}
heliox tool signnow -- invite send <document-id> \
  --to '[{"email":"signer@acme.com","role":"Signer 1","order":1}]' \
  --subject "Please sign" --message "Thanks!"

# free-form invite for a document WITHOUT fields: a single --email recipient
heliox tool signnow -- invite send <document-id> --email signer@acme.com
```

`invite send` resolves the required sender ("from") from your authenticated
account automatically; pass `--from <email>` to override. Add `--no-email` to
suppress SignNow's outbound signer email (embedded-style flow).

### Track & recall

```bash
heliox tool signnow -- invite resend <field-invite-id>          # nudge a pending signer
heliox tool signnow -- invite cancel <document-id>              # recall a sent document
```

Get the `<field-invite-id>` from `document get` (each entry under
`field_invites` carries its `id`, `email`, and `status`).

### Deliver the signed artifact

```bash
heliox tool signnow -- document download <document-id> --out ./signed.pdf
heliox tool signnow -- document download <document-id> --out ./signed.pdf --with-history
```

### Templates & signing links

```bash
heliox tool signnow -- template create <document-id> --name "NDA Template"   # document → template
heliox tool signnow -- template copy <template-id> --name "Acme NDA"         # template → fresh document
heliox tool signnow -- link create <document-id>                              # signing link (no known signer email)
```

Run `-- <resource> <verb> --help` for the exact flags rather than guessing.

## Footguns

- **Free-form (`--email`) invites work only on documents WITHOUT fields.** A
  fielded document needs a role-based `--to` field invite; SignNow rejects a
  free-form invite on it, and the tool surfaces that error rather than guessing.
- **`document list` already covers freshly-uploaded docs.** If a doc you just
  uploaded seems missing, re-run `document list` (not `document get` on a
  guessed id): the merged list includes the un-edited leg.
- **`invite cancel` takes the DOCUMENT id; `invite resend` takes the FIELD
  INVITE id.** They are different ids. Read the invite id from `document get`.
- **`--account` when more than one SignNow account is connected.** A `409`
  lists candidate account keys; re-run with `--account <key>` before the `--`.

## Safety

- Sending an invite emails an external signer and starts a legally-binding
  signature flow: it is an outward-facing action. Follow the sensitive-
  operation rule in [../SKILL.md](../SKILL.md): confirm the recipient list and
  document before sending, and prefer showing the user the prepared document
  (`document get`) first.
- `link create` mints a signing link anyone with the URL can use: treat it as
  sensitive and share it only as the user intends.
