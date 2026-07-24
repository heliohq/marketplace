# Crisp (`heliox tool crisp`)

Crisp is a customer-support platform (live-chat widget, shared inbox, People
CRM). This tool works one **website** (Crisp's word for a workspace) at a time:
inbox conversations, their messages, and contacts.

Read `../SKILL.md` first for the connect/use/error model shared by every tool.

## Connect (key entry, not OAuth)

Crisp has no OAuth for this; the credential is a **website token keypair**. Ask
the workspace **owner** to generate one: Crisp dashboard → Settings → Workspace
Settings → Advanced configuration → API Token → **Generate Token** (no
Marketplace account needed; owner-only; shown once). It is an
`identifier` + `key` pair.

```bash
heliox tool crisp auth --json      # mints the connect link; relay it to the user
```

On the connect page the user pastes the keypair as a single
**`identifier:key`** string (exactly Crisp's own `curl --user "id:key"` shape).
Helio stores it encrypted and checks it on first use.

## `--website` is required on every command

Every Crisp route is scoped to a `website_id`, and a website token cannot list
websites — so **you must pass `--website <id>` on every call**. There is no
auto-resolve. Find the `website_id` in the Crisp dashboard URL (the UUID after
`website/`) or in workspace settings; ask the user once, then **carry the same
`website_id` across the whole session**.

## Command surface

Everything after `--` goes to the tool. Every verb needs `--website <id>` and
prints a single JSON object `{ "data": <crisp payload>, "meta": {...} }`.

```bash
# Triage the inbox (newest page 1; --filter-status resolved|unresolved)
heliox tool crisp -- conversation list --website <id> [--page N] [--filter-status resolved]

# Read one thread and its messages
heliox tool crisp -- conversation get      --session <session_id> --website <id>
heliox tool crisp -- conversation messages --session <session_id> --website <id> [--before <unix_ms>]

# Reply to the customer (from operator by default; --from user to speak as the visitor)
heliox tool crisp -- conversation reply --session <session_id> --text "..." --website <id>

# Resolve / reopen, and assign to an operator
heliox tool crisp -- conversation state --session <session_id> --state resolved|pending|unresolved --website <id>
heliox tool crisp -- conversation route --session <session_id> --operator <user_id|email> --website <id>

# Contacts (People)
heliox tool crisp -- people list   --website <id> [--page N] [--search "<text>"]
heliox tool crisp -- people get    --people <people_id> --website <id>
heliox tool crisp -- people create --email <email> [--nickname "<name>"] --website <id>
```

Notes:

- **`conversation messages` paginates by time, not page.** The default returns
  the latest messages; pass `--before <unix_ms>` (a message timestamp) to walk
  backwards through history.
- **`conversation route --operator`** accepts either a raw operator `user_id`
  **or** an email. An email triggers one extra lookup against the website's
  operator list to resolve the `user_id`; an email with no matching operator
  fails with a clear error (nothing is assigned).
- `--help` after `--` is the per-command reference for any flag not shown here.

## Safety

`conversation reply`, `conversation state`, `conversation route`, and
`people create` change or send data in the user's live support workspace —
outward-facing actions. Follow the sensitive-operation rule in
`../SKILL.md`: confirm the target conversation and the message text
before sending a reply, and confirm before resolving or reassigning a thread.
