# Adobe Acrobat Sign (`heliox tool adobe-sign -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Adobe Acrobat
Sign is a **flat provider**: everything after `--` is the adobe-sign tool's own
CLI, grouped by resource (`agreement`, `library`, `document`).

```bash
heliox tool adobe-sign [--account <key>] -- <resource> <verb> [flags...]
```

The unit of work is an **agreement**: a document sent to one or more recipients
for signature, tracked to completion, then retrieved. Pass `--json` on any
command for a stable, provider-neutral envelope (snake_case fields).

## The send / track / retrieve / cancel loop

Send a document for signature — either a local file (uploaded automatically) or
a reusable library document (template):

```bash
# From a local file (two steps happen internally: transient upload -> create):
heliox tool adobe-sign -- agreement send \
  --document ./contract.pdf \
  --recipient-email signer@example.com --recipient-name "Sam Signer" \
  --name "Q3 Contract" --json
# -> {"agreement_id":"CBJ...","status":"IN_PROCESS"}

# From a reusable library document / template (no file upload):
heliox tool adobe-sign -- agreement send \
  --library-id <libraryDocumentId> \
  --recipient-email signer@example.com --name "NDA" --json
```

Check status and per-participant progress:

```bash
heliox tool adobe-sign -- agreement list --json          # what's out / completed (--cursor, --page-size)
heliox tool adobe-sign -- agreement get <id> --json      # one agreement's status (e.g. OUT_FOR_SIGNATURE, SIGNED)
heliox tool adobe-sign -- agreement members <id> --json  # per-signer status
```

Retrieve the completed PDF, or cancel an agreement sent in error:

```bash
heliox tool adobe-sign -- agreement download <id> --out ./signed.pdf
heliox tool adobe-sign -- agreement cancel <id> --comment "sent in error" --json
```

## Library documents (templates) and raw uploads

```bash
heliox tool adobe-sign -- library list --json            # reusable templates
heliox tool adobe-sign -- library get <id>
heliox tool adobe-sign -- document upload ./file.pdf     # -> a transient document id
```

`agreement send --document` performs the upload for you; `document upload` is
only for callers that want the transient id explicitly.

## Status values

Adobe's status enums pass through verbatim in the `status` field
(`OUT_FOR_SIGNATURE`, `SIGNED`, `CANCELLED`, `WAITING_FOR_MY_SIGNATURE`, …).
Treat `SIGNED` as complete; `agreement download` returns the combined signed
PDF once the agreement reaches that state.

## Notes

- **Errors** render as `{"error":{"code":"api_error|usage","message":"…","status":<HTTP>}}`
  under `--json`; exit code is 0 success, 1 API/runtime failure, 2 usage error.
- **60-day idle re-auth.** Adobe's refresh token expires after 60 days of
  inactivity. If nobody has used the Adobe Sign connection for two months, the
  connection dies and the user must reconnect (`heliox tool adobe-sign auth`).
  Nothing to do in-band — just re-send the authorize link if a call reports the
  connection needs reconnecting.
