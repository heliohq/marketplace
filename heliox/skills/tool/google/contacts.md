# Google Contacts (`heliox tool google contacts -- ...`)

Read [google.md](./google.md) for auth and account selection. Everything after
`--` is the contacts tool's own CLI. This tool is **read-only** (v1): it reads
and searches contacts, it never creates, edits, or deletes them.

Its reason to exist is resolving a name to an email/phone so you can act on it
(e.g. hand the address to `gmail drafts create`).

## Resolve first

For "email/message/invite <person>", always start with `resolve`: one call that
covers **both** My Contacts and Gmail's auto-collected Other Contacts. Do not
call the two searches yourself.

```bash
heliox tool google contacts -- resolve "Zhang San" --json
```

- `.matches[]` carries `name`, `emails`, `phones`, `organization`, and `source`
  (`my_contact` | `other_contact`, My Contacts listed first).
- **Zero matches** exits with a distinct non-zero code and prints "no contacts
  matched …": it is an empty result, not an error. Try a shorter prefix
  (surname or first name), then fall back (see below). Do not retry the same
  query.
- **Multiple candidates: never silently pick one.** List them and let the user
  choose before sending anything. Emailing the wrong person is the most
  expensive mistake here.

## Reading and searching

```bash
heliox tool google contacts -- list --max 50 --sort last-modified --json   # people.connections.list
heliox tool google contacts -- get people/c123 people/c456 --json          # people.get / getBatchGet
heliox tool google contacts -- search --query "zhang" --max 30 --json       # My Contacts
heliox tool google contacts -- other list --json                            # Gmail auto-collected addresses
heliox tool google contacts -- other search --query "zhang" --json
heliox tool google contacts -- groups list                                  # contact groups (labels)
heliox tool google contacts -- groups get contactGroups/family
```

## Search semantics (prefix phrase)

- Search matches **prefix phrases**, not substrings: "foo name" is found by
  "f", "foo", "foo n", "nam", but **not** "oo n". If a search misses, retry
  with a shorter prefix, not a middle fragment.
- `--max` is capped at **30** (People API hard limit); higher values are
  silently clamped.
- `search` (My Contacts) matches names / nicknames / emails / phones /
  organizations. `other search` (Other Contacts) matches only names / emails /
  phones: searching Other Contacts by organization returns nothing.
- Freshness: search runs off a cache with a minute-scale propagation delay. A
  just-added contact may not be searchable yet: that is expected. Use
  `list --sort last-modified` or try again shortly rather than insisting the
  contact is missing.

## Cross-app flow: resolve → send

"Send the weekly report to Zhang San":

```bash
heliox tool google contacts -- resolve "Zhang San" --json      # → zhangsan@corp.com (or several candidates → ask)
heliox tool google gmail -- drafts create --to zhangsan@corp.com --subject "Weekly report" --body-file ./weekly.md --json
```

Contacts and Gmail are **two separate connections with two separate consents**.

- **Contacts connected** → always resolve addresses with `contacts resolve`;
  do not guess from mail history.
- **Contacts not connected** → fall back to Gmail's own search
  (`gmail -- messages list --query 'from:Zhang San'`) to dig an address out of
  past mail, and at a natural moment suggest connecting Google Contacts
  (`heliox tool google auth contacts`) for more reliable resolution, without
  blocking the current task.
- Actually sending is approval-gated: see gmail.md's "Sending email goes
  through the approval gate".

## Read-only

This tool cannot change the address book. If the user asks you to "save Zhang
San to my contacts", add a note, or apply a label, say plainly that it is not
supported yet. Do not reach for another write path to work around it.
