# Help Scout (`heliox tool help-scout -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Help Scout is
a **flat provider** (not grouped like `google`): everything after `--` is the
help-scout tool's own CLI, run against the Help Scout Mailbox (Inbox) API 2.0.

```bash
heliox tool help-scout [--account <key>] -- <resource> <verb> [flags...]
```

You are a support teammate working a shared inbox: triage the queue, read a
conversation with its threads, answer the customer or leave an internal note,
and move the conversation's state. Reads return Help Scout's HAL JSON
(`_embedded`, `page`, `_links`) verbatim so pagination stays visible; writes
that create or mutate return a small `{"id":..., "status":...}` receipt.

## The mental model (read this first)

- A **conversation** lives in one **inbox** (Help Scout calls it a mailbox) and
  has a **status** (`active` / `pending` / `closed` / `spam`), an optional
  **assignee**, **tags**, and a **primary customer**.
- Its content is a list of **threads**: customer messages, staff **replies**
  (outward-facing, emailed to the customer), and internal **notes** (team-only,
  never sent to the customer).
- Answering the customer = `thread reply`. Leaving a team-only comment =
  `thread note`. Do not confuse them: a reply leaves your account.

## Core commands

### Triage the queue

```bash
# list/filter/search; every filter is optional (API defaults to status=active)
heliox tool help-scout -- conversation list --mailbox <id> --status active --json
heliox tool help-scout -- conversation list --tag vip --assigned-to <user-id> --json
heliox tool help-scout -- conversation list --modified-since 2026-07-01T00:00:00Z --json

# advanced search: --query is Help Scout's Lucene-style string, passed through verbatim
heliox tool help-scout -- conversation list --query 'modifiedAt:[NOW-1HOUR TO *]' --json
heliox tool help-scout -- conversation list --query 'assigned:"Unassigned" tag:"urgent"' --json
```

Sort with `--sort-field` (`modifiedAt`, `createdAt`, `number`, `subject`, …)
and `--sort-order asc|desc`; page with `--page <n>`.

### Read before you answer

```bash
heliox tool help-scout -- conversation get <id> --embed-threads --json   # conversation + its threads
heliox tool help-scout -- thread list <conversation-id> --json           # just the threads, paginated
```

### Answer

```bash
# reply to the customer; --customer-id defaults to the conversation's primary
# customer (one extra lookup) when omitted. Set status/assignee in the same call.
heliox tool help-scout -- thread reply <conversation-id> --text "Here's the fix..." --status closed --json
heliox tool help-scout -- thread reply <conversation-id> --text "Draft for review" --draft --json
heliox tool help-scout -- thread reply <conversation-id> --text "..." --cc "a@x.com,b@x.com" --json

# internal note for the team (never sent to the customer)
heliox tool help-scout -- thread note <conversation-id> --text "Escalated to eng, see JIRA-123" --json
```

### Move conversation state

```bash
# status / assignee / subject — flags compile to the API's JSON-Patch ops for you
heliox tool help-scout -- conversation update <id> --status pending --json
heliox tool help-scout -- conversation update <id> --assign-to <user-id> --json
heliox tool help-scout -- conversation update <id> --unassign --json

# tags REPLACE the whole set (empty --tags clears every tag)
heliox tool help-scout -- conversation tag <id> --tags "vip,billing" --json

# snooze until a future time; --unsnooze-on-customer-reply defaults to true
heliox tool help-scout -- conversation snooze <id> --until 2026-07-25T09:00:00Z --json
heliox tool help-scout -- conversation unsnooze <id> --json
```

### Create a conversation

```bash
# an inbox id, a subject, a customer (email or id), and initial --text are required;
# --status defaults to active; --type defaults to email
heliox tool help-scout -- conversation create --mailbox <id> --subject "Refund request" \
  --customer-email person@example.com --text "Logging the customer's request" --json
```

### Customers, inboxes, saved replies, tags, users

```bash
heliox tool help-scout -- customer list --query "email:person@example.com" --json
heliox tool help-scout -- customer get <id> --json
heliox tool help-scout -- customer create --first-name Ada --last-name Lovelace --email ada@x.com --json
# partial update — only the fields you pass change; omitted fields are preserved
heliox tool help-scout -- customer update <id> --job-title "VP Sales" --json

heliox tool help-scout -- inbox list --json                 # inbox (mailbox) ids for --mailbox
heliox tool help-scout -- inbox folders <inbox-id> --json

heliox tool help-scout -- saved-reply list --inbox <id> --json      # canned answers for consistent drafting
heliox tool help-scout -- tag list --json
heliox tool help-scout -- user list --json
heliox tool help-scout -- user me --json                    # the connected Help Scout user
```

Run `-- <resource> --help` (or `-- <resource> <verb> --help`) for exact flags
rather than guessing.

## Footguns (where agents go wrong)

- **Reply vs. note.** `thread reply` is outward-facing — it emails the
  customer. `thread note` is team-only. Pick deliberately; when unsure, use a
  note or a `--draft` reply.
- **`conversation tag` replaces the entire set.** To add one tag you must send
  the full desired set (read the conversation first). An empty `--tags` clears
  all tags.
- **`--mailbox` is an inbox id, not a name.** Run `inbox list` first to get the
  numeric id; `conversation create` and several filters need it.
- **Snooze always sends both fields.** `--until` is required and must be a
  future ISO-8601 timestamp; `--unsnooze-on-customer-reply` defaults to `true`
  (the conversation wakes if the customer writes back). Snooze is its own
  endpoint — you cannot set it through `conversation update`.
- **Create needs a customer and an initial message.** Pass one of
  `--customer-email` / `--customer-id` and a non-empty `--text`.
- **Writes return a receipt, not the resource.** `create` / `reply` / `note`
  answer `{"id":"<new-id>","status":"created"}`; `update` / `tag` / `snooze`
  answer a status receipt with no body. Re-`get` the conversation if you need
  the full updated object.
- **`--account` when more than one Help Scout account is connected.** A `409`
  lists candidate account keys; re-run with `--account <key>` before the `--`.

## Safety

- Replies and newly created conversations leave your account and reach real
  customers — follow the sensitive-operation rule in [../SKILL.md](../SKILL.md).
  Prefer `--draft` on a reply when you want a human to review before it sends.
- `conversation update --status spam` and destructive state changes should be
  confirmed with the user before running against a live inbox.
