# DocuSign (`heliox tool docusign -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. DocuSign is a
**flat provider**: everything after `--` is the DocuSign tool's own CLI,
speaking the eSignature REST API v2.1 with the connected user's OAuth token.
The account-scoped API base (region host + account id) is resolved for you at
connect time, so you never pass it.

```bash
heliox tool docusign [--account <key>] -- <resource> <verb> [flags...]
```

Resources: `envelope` (send / list / get / recipients / void / download) and
`template` (list / get). Run `-- <resource> <verb> --help` for the full flags.

## The loop: send → track → retrieve

**Send a document out for signature.** Two ways; a reusable template (clean,
preferred when one exists) or a local file:

```bash
# From a template: fill one role with the signer
heliox tool docusign -- envelope send \
  --template-id <id> --signer-email ada@acme.com --signer-name "Ada Lovelace" \
  --subject "Please sign the NDA"

# From a document: a signature tab is anchored on the text /sn1/ by default
heliox tool docusign -- envelope send \
  --document ./contract.pdf --signer-email ada@acme.com --signer-name "Ada Lovelace"
```

Add `--draft` to create the envelope without sending it. List templates first
to get an id: `heliox tool docusign -- template list`.

**Track status**: "has it been signed yet?"

```bash
heliox tool docusign -- envelope list --status sent            # what's out for signature
heliox tool docusign -- envelope list --status completed        # what finished
heliox tool docusign -- envelope get <envelope-id>              # one envelope's status
heliox tool docusign -- envelope recipients <envelope-id>       # per-signer status + signed_at
```

`envelope list` defaults to the last 30 days; pass `--from-date YYYY-MM-DD` to
widen it and `--count N` to cap results. Common statuses: `sent`, `delivered`,
`completed`, `declined`, `voided`.

**Retrieve the signed PDF** once completed:

```bash
heliox tool docusign -- envelope download <envelope-id> --out ./signed.pdf
```

Omit `--out` to stream the PDF bytes to stdout.

**Void** an envelope sent in error (a reason is required):

```bash
heliox tool docusign -- envelope void <envelope-id> --reason "sent to the wrong signer"
```

## Notes

- Output is provider-neutral snake_case JSON with `--json`; the default is a
  one-line-per-row human summary.
- All commands act on the user's **default** DocuSign account. Multi-account
  selection is not exposed in this version.
- Only `sent`/draft envelopes can be voided; a `completed` one cannot.
