# Jotform (`heliox tool jotform -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Jotform is a
**flat provider** (not grouped like `google`): everything after `--` is the
jotform tool's own CLI.

```bash
heliox tool jotform [--account <key>] -- <resource> <verb> [flags...]
```

## Connect

Jotform authenticates with a **personal API key**, not OAuth. `heliox tool
jotform auth` gives the user a link to paste their key; they mint one at
**My Account → Settings → API → Create New Key** (or
https://www.jotform.com/myaccount/api). Two things to know:

- A key is **Read Only** or **Full Access**, chosen when it is created. Read
  verbs work with either; **write verbs (`submission create/edit/delete`) need a
  Full Access key**. A read-only key returns Jotform's `401 "You're not
  authorized to use ..."` on a write — surfaced verbatim. If you hit it, tell
  the user to create a Full Access key and reconnect.
- Keys are **US-account only** here. An EU- or HIPAA-residency account's key
  will fail to connect (it authenticates only against its own region's base).

Every command prints Jotform's native envelope
(`{"responseCode":200,"message":"success","content":{...}}`) — read `content`.

## The qid recipe (read this first)

A form's answers are keyed by **question id (qid)**, not by field label. To read
or write submission values correctly, get the qids first:

```bash
heliox tool jotform -- form list --json                 # find the form id
heliox tool jotform -- form questions <formID> --json   # qid → field, per question
heliox tool jotform -- form submissions <formID> --json # existing responses, keyed by qid
```

Then create/edit answers by qid (below).

## Core commands

### Account

```bash
heliox tool jotform -- user            # account identity (also the connect verifier)
heliox tool jotform -- usage           # API-call quota + submission/upload counts
```

### Forms & responses (read)

```bash
heliox tool jotform -- form list [--limit N --offset N --filter '<json>' --orderby created_at]
heliox tool jotform -- form get <formID>
heliox tool jotform -- form questions <formID>
heliox tool jotform -- form submissions <formID> [--limit N --offset N --filter '<json>' --orderby created_at]
heliox tool jotform -- submission list [--limit N --offset N ...]   # across all forms
heliox tool jotform -- submission get <submissionID>
heliox tool jotform -- report list [--form <formID>]               # shareable report views
heliox tool jotform -- folder list
```

`--filter` takes a Jotform JSON filter object, e.g.
`--filter '{"status":"ENABLED"}'`. `--limit`/`--offset` page results (Jotform
caps at 1000 per page).

### Submissions (write — Full Access key)

Answers are passed as repeatable `--field qid=value`. For **composite** fields
(name, address, …) address a subfield with `qid:subfield=value`:

```bash
# simple + composite fields in one create
heliox tool jotform -- submission create <formID> \
  --field 3="Ada Lovelace" \
  --field 5:first="Ada" --field 5:last="Lovelace" \
  --field 7="ada@example.com"

heliox tool jotform -- submission edit <submissionID> --field 3="Grace Hopper"
heliox tool jotform -- submission delete <submissionID>
```

The `--field` value splits on the **first** `=`, so a value may contain `=`.
Get the qids from `form questions <formID>` before writing.

## Footguns

- **A submission created via the API does not fire the form's email
  notifications or integrations** — it lands in the submission list silently.
  Set expectations if the user is relying on a notification.
- **Read-only key on a write** → Jotform `401 not authorized`, surfaced
  verbatim. It is a key-permission problem, not a bad key: the user needs a Full
  Access key. It does **not** disconnect the account.
- **Guessing field keys** — never write `--field <label>=...`; Jotform ignores
  anything that is not a real qid. Always read `form questions` first.

## Safety

Creating, editing, or deleting a submission changes the user's Jotform data —
an outward-facing action. Follow the sensitive-operation rule in
[../SKILL.md](../SKILL.md): confirm before writing, and
never delete a submission without explicit user intent.
