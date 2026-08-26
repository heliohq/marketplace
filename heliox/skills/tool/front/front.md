# Front (`heliox tool front -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Front is a
**flat provider** (not grouped like `google`): everything after `--` is the
front tool's own CLI.

```bash
heliox tool front [--account <key>] -- <resource> <verb> [flags...]
```

Front is a shared-inbox / customer-communication platform: teams triage
customer conversations from shared inboxes, assign/tag/snooze them, reply, and
coordinate internally with private comments. Work it the way a human agent
does: read the queue, decide what matters, draft or send a reply, leave an
internal comment for a colleague, and tag/assign/archive.

The connection is **company-scoped** (one Front company, not a personal
mailbox): `front -- me` shows which company the token belongs to.

## Output shape (every command)

Every command emits a provider-neutral envelope on stdout, never the raw Front
body:

- List commands: `{"data":[…],"next_page_token":"<cursor|empty>"}`. Pass the
  cursor back with `--page-token` to get the next page; an empty
  `next_page_token` means you have reached the end.
- Single-object commands: `{"data":{…}}`.
- Mutations with no return body (update / assign / tag): `{"data":{"ok":true}}`.

You never handle Front URLs: the tool lifts the opaque cursor out of Front's
pagination link and hands it to you as `next_page_token`.

## Read the queue

```bash
# list the visible queue (most recent first with --sort-order desc)
heliox tool front -- conversation list --limit 20 --json
heliox tool front -- conversation list --inbox <inbox_id> --limit 20 --json   # one inbox
heliox tool front -- conversation list --q "refund" --json                    # keyword search
heliox tool front -- conversation list --page-token <cursor> --json           # next page

# one conversation's metadata, its message thread, its internal comments
heliox tool front -- conversation get --id <cnv_id> --json
heliox tool front -- conversation messages --id <cnv_id> --json
heliox tool front -- conversation comments --id <cnv_id> --json
```

## Reply, draft, comment

```bash
# reply into an existing conversation (this does NOT start a new conversation)
heliox tool front -- message send --conversation <cnv_id> --body "Thanks, refunded." --json
#   --text "<plain>"  plain-text alternative body
#   --author <teammate_id>  send on behalf of a teammate
#   --channel <channel_id>  send from a specific channel (defaults to the conversation's)

# draft a reply for a human to review/send, the SAFER default over auto-sending
heliox tool front -- draft create --conversation <cnv_id> --body "Draft reply" --channel <channel_id> --json

# leave an internal comment (@mention a teammate inside the body)
heliox tool front -- comment add --conversation <cnv_id> --body "@alex can you confirm the refund?" --json
```

Prefer **`draft create`** when a human should review before it goes out; use
**`message send`** only when you are meant to send directly.

## Triage: status, assignee, tags

`conversation update` presents one intent but issues the distinct calls Front
needs under the hood. Combine any of them in one command:

```bash
heliox tool front -- conversation update --id <cnv_id> --status archived --json
heliox tool front -- conversation update --id <cnv_id> --status open --json          # reopen
heliox tool front -- conversation update --id <cnv_id> --status spam --json
heliox tool front -- conversation update --id <cnv_id> --assignee <teammate_id> --json
heliox tool front -- conversation update --id <cnv_id> --assignee null --json         # unassign
heliox tool front -- conversation update --id <cnv_id> --tag-add <tag_id> --tag-remove <tag_id> --json
```

Valid `--status`: `open`, `archived`, `deleted`, `spam`.

## Resolve ids (contacts, inboxes, teammates, tags)

```bash
heliox tool front -- contact list --q "jane@example.com" --json
heliox tool front -- contact get --id alt:email:jane@example.com --json   # by handle alias
heliox tool front -- contact create --name "Jane Doe" --handle email:jane@example.com --json
heliox tool front -- inbox list --json        # discover inbox ids for conversation list --inbox
heliox tool front -- teammate list --json     # resolve assignee target ids
heliox tool front -- tag list --json          # resolve tag ids for --tag-add / --tag-remove
heliox tool front -- me --json                # the Front company this connection is scoped to
```

Run `-- <resource> <verb> --help` for exact flags rather than guessing.

## Footguns

- **`message send` is a reply, not a new conversation.** It always replies into
  an existing `--conversation`. Starting a brand-new outbound conversation
  (which needs a channel) is intentionally out of scope for v1.
- **`draft create` requires `--channel`.** A draft must know which channel it
  would be sent from; get channel ids via `inbox list` (or the conversation's
  own metadata). A reply (`message send`) does not need one.
- **Ids come from the resolve commands.** `--assignee` wants a teammate id
  (`teammate list`), `--tag-add`/`--tag-remove` want tag ids (`tag list`),
  `--inbox` wants an inbox id (`inbox list`). Names are not accepted.
- **`--assignee null` unassigns**: an empty value or the literal `null` clears
  the assignee.
- **Pagination is cursor-based.** Do not try to reconstruct Front URLs; page
  only with the `next_page_token` the tool gives you, via `--page-token`.
- **`--account` when more than one Front company is connected.** A `409` lists
  the candidate account keys; re-run with `--account <key>` before the `--`.

## Safety

- Sending a reply (`message send`) is an outward-facing action that reaches a
  real customer: follow the sensitive-operation rule in
  [../SKILL.md](../SKILL.md), and prefer `draft create` when a human should
  review first.
- Internal comments (`comment add`) are visible to the whole team on that
  conversation; write them as you would a note to a colleague.
- Never echo tokens; the CLI never shows them to you by design.
