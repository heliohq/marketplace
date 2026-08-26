# Freshdesk (`heliox tool freshdesk -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Freshdesk is a
**flat provider** (not grouped like `google`): everything after `--` is the
freshdesk tool's own CLI, run against the Freshdesk v2 REST API. Output is the
provider's JSON response, verbatim.

```bash
heliox tool freshdesk [--account <domain>] -- <resource> <verb> [flags...]
```

## Connect requires TWO things: domain + API key

Freshdesk's API lives at a **per-account base URL**
`https://<domain>.freshdesk.com/api/v2`. The `<domain>` subdomain is not
derivable from the key, so connecting Freshdesk asks for **both**:

- **Domain**: e.g. `acme.freshdesk.com` (the account subdomain). This is the
  connection's account key; when a user has more than one Freshdesk connected,
  select with `--account <domain>` before the `--`.
- **API key**: from Freshdesk **Profile Settings -> View API key**. Long-lived,
  non-expiring; resetting it in Freshdesk revokes the connection (a later call
  returns a rejected-credential error → ask the user to reconnect).

If the tool isn't connected yet, run `heliox tool freshdesk auth` and give the
user the connect link. The key is injected per call; it never passes through you.

## The core loop: triage and answer tickets

```bash
# read the open queue (predefined filters: new_and_my_open|watching|spam|deleted)
heliox tool freshdesk -- ticket list --filter new_and_my_open --per-page 30

# find whether an open ticket already exists (Freshdesk query language, quoted)
heliox tool freshdesk -- ticket search --query "status:2 AND priority:4"
heliox tool freshdesk -- ticket search --query "requester_id:123 AND status:2"

# open one ticket in full, with its thread and requester embedded
heliox tool freshdesk -- ticket get --id 4021 --include conversations,requester

# reply to the CUSTOMER (public, emailed to the requester)
heliox tool freshdesk -- ticket reply --id 4021 --body "<p>Thanks, shipping a fix today.</p>"

# add an INTERNAL note (private by default; not visible to the requester)
heliox tool freshdesk -- ticket note --id 4021 --body "<p>Root-caused to the webhook retry.</p>"
heliox tool freshdesk -- ticket note --id 4021 --body "<p>Customer-visible FYI</p>" --public

# change status / priority / assignment / tags
heliox tool freshdesk -- ticket update --id 4021 --status 4 --responder-id 55
```

Status codes: `2` Open, `3` Pending, `4` Resolved, `5` Closed.
Priority codes: `1` Low, `2` Medium, `3` High, `4` Urgent.

`reply` and `note` bodies are **HTML** (`<p>...</p>`), not plain text: the API
renders them as rich content.

## Contacts, companies, agents

```bash
# resolve who a requester is (or create/correct a contact)
heliox tool freshdesk -- contact search --query "email:'jane@acme.com'"
heliox tool freshdesk -- contact get --id 987
heliox tool freshdesk -- contact create --name "Jane Roe" --email jane@acme.com --company-id 42

# B2B account context ("what else is open for this company?")
heliox tool freshdesk -- company get --id 42
heliox tool freshdesk -- company search --query "name:'Acme'"

# route/assign to the right agent; me is also the connectivity/identity check
heliox tool freshdesk -- agent list
heliox tool freshdesk -- agent me
```

Run `-- <resource> <verb> --help` for the exact flags rather than guessing.

## Footguns

- **`ticket create` only requires a requester (`--email` OR `--requester-id`).**
  `--subject`, `--description`, `--status`, and `--priority` are all optional:
  Freshdesk defaults status to `2` (Open) and priority to `1` (Low) when they
  are omitted, so a create with just a requester succeeds (it does NOT return a
  `400`). Still, pass explicit `--status`/`--priority` (and a `--subject`) as
  good practice so the ticket lands in the state and queue you intend. Example:

  ```bash
  heliox tool freshdesk -- ticket create --subject "Login fails" \
    --description "<p>500 on sign-in</p>" --email jane@acme.com \
    --status 2 --priority 1
  ```

- **`ticket update --tags` REPLACES the whole tag set.** It is the full desired
  set, not an add: there is no client-side merge. Read the current tags first
  (`ticket get`) if you need to preserve existing ones.

- **Notes are PRIVATE by default.** `ticket note` writes an internal note; pass
  `--public` only when you intend the requester to see it. `ticket reply` is
  always customer-visible (it emails them). Use it deliberately.

- **Search is quoted Freshdesk query syntax, and string values need inner
  quotes**: `--query "email:'jane@acme.com'"`, `--query "status:2 AND
  priority:4"`. Search is capped at 10 pages (`--page 1..10`).

- **Pagination is explicit and not auto-followed.** `--page` / `--per-page`
  (default 30, max 100) pass through; the tool does not walk all pages, so a
  large queue needs paging by you.

- **`--account <domain>` when more than one Freshdesk is connected.** A conflict
  lists the candidate domains; re-run with `--account <domain>` (before the `--`).

## Safety

- `ticket reply` emails the customer and `ticket note --public` is
  requester-visible. Both are outward-facing. Follow the sensitive-operation
  rule in [../SKILL.md](../SKILL.md) before writing into a real support queue,
  especially on tickets you did not open.
