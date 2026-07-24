# Missive (`heliox tool missive -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Missive is a
**flat provider** (not grouped like `google`): everything after `--` is the
missive tool's own CLI. Missive is a collaborative **shared inbox** — a team
works email/SMS/chat out of shared accounts, with internal comments threaded
next to customer messages.

```bash
heliox tool missive [--account <key>] -- <resource> <verb> [flags...]
```

Auth is a **personal API token** (not OAuth): the user pastes a `missive_pat-…`
token once (Missive → Preferences → API, Productive plan required); the CLI
injects it as `Authorization: Bearer` on every call. Output is **always JSON**
(provider pass-through); `--json` is accepted for uniformity and only toggles
the error format.

## The teammate loop

1. **Triage** a mailbox → `conversations list`.
2. **Read a thread** → `conversations messages|comments|posts <id>`.
3. **Leave an internal note** → `posts create` (a post = a comment/annotation).
4. **Reply to the customer** → `drafts create` (add `send:true` to send).
5. **Change state** (close / assign / label) → `conversations update <id>`.
6. **CRM sync** → `contacts …` within a `contact-books`.

## Core commands

### Triage + read

```bash
# List a mailbox — ONE mailbox filter is REQUIRED (see footguns)
heliox tool missive -- conversations list --inbox --limit 25
heliox tool missive -- conversations list --assigned
heliox tool missive -- conversations list --shared-label <label-id>
heliox tool missive -- conversations list --team-inbox <team-id>

# One conversation, then its thread (messages / internal comments / posts)
heliox tool missive -- conversations get <conversation-id>
heliox tool missive -- conversations messages <conversation-id> --limit 10
heliox tool missive -- conversations comments <conversation-id>
heliox tool missive -- conversations posts    <conversation-id>
```

### Write (post / draft / state change)

Write bodies are **verbatim passthrough** — you supply the full Missive
envelope. Pass it inline with `--body '<json>'` or from a file with
`--file <path|->` (`-` = stdin).

```bash
# Internal note into a conversation
heliox tool missive -- posts create --body '{"posts":{"conversation":"<cid>","text":"Summary for the team","notification":{"title":"AI","body":"triaged"}}}'

# Reply draft (omit send to leave it as a draft; add "send":true to send)
heliox tool missive -- drafts create --body '{"drafts":{"conversation":"<cid>","body":"Thanks — looking into it.","from_field":{"address":"support@acme.com"},"to_fields":[{"address":"cust@x.com"}],"send":true}}'

# Change state: close / assign / (un)label via PATCH
heliox tool missive -- conversations update <cid> --body '{"conversations":{"add_shared_labels":["<label-id>"],"close":true}}'
```

### Contacts (CRM sync)

```bash
# contact-book id is REQUIRED for contacts list
heliox tool missive -- contact-books list
heliox tool missive -- contacts list --contact-book <cb-id> --search "acme" --limit 50
heliox tool missive -- contacts get <contact-id>
heliox tool missive -- contacts create --body '{"contacts":[{"contact_book":"<cb-id>","first_name":"Ada"}]}'
heliox tool missive -- contacts update <id-or-comma-ids> --body '{"contacts":[{"last_name":"Lovelace"}]}'
```

## Pagination (two shapes — not uniform)

List verbs emit `{"items":[...], "next_offset"|"next_until": <cursor|null>}`.
You decide when to fetch more; nothing auto-pages.

- **Conversations + messages/comments/posts** use a timestamp cursor: the reply
  carries `next_until`. Feed it back via `--until <value>`. A page may return
  **more** than `--limit`, so page on `next_until` until it is `null`, never on
  the item count.
- **Contacts + contact-books** use `next_offset`; feed it back via `--offset`.

## Footguns (where agents go wrong)

- **`conversations list` needs a mailbox filter.** Missive rejects a bare list
  with a 400 (`"You need to paginate at least one mailbox"`). Pass exactly one
  of `--inbox / --all / --assigned / --closed / --snoozed / --flagged /
  --trashed / --junked / --drafts / --shared-label <id> / --team-inbox <id> /
  --team-all <id> / --team-closed <id>`.
- **Narrowing filters are mutually exclusive.** `--email`, `--domain`, and
  `--contact-organization` cannot be combined — the CLI rejects the combo
  before calling (exit 2).
- **`contacts list` requires `--contact-book`.** It is a required flag; get ids
  from `contact-books list`.
- **Write bodies are the full envelope.** posts create wraps under `posts`,
  drafts under `drafts`, conversations update under `conversations`, contacts
  under a `contacts` **array**. The CLI passes your JSON through unchanged — it
  does not add the wrapper for you.
- **A send is a draft with `send:true`.** There is no separate send verb; drafts
  create with `send:true` sends immediately (email or SMS).
- **201 with no body → `{"ok":true}`.** Some writes return an empty success;
  the CLI normalizes that so you always get JSON.
- **`--account` when more than one Missive token is connected.** A 409 lists
  candidate account keys; re-run with `--account <key>` before the `--`.

## Safety

- Drafts sent with `send:true` and posts are outward/team-facing — follow the
  sensitive-operation rule in [../SKILL.md](../SKILL.md) before writing into a
  shared inbox others read. Prefer an internal `posts create` note over a
  customer-visible send when you are unsure.
