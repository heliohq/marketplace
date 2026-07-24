# Apollo.io (`heliox tool apollo -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Apollo is a
**flat provider** (not grouped like `google`): everything after `--` is the
apollo tool's own CLI.

```bash
heliox tool apollo [--account <key>] -- <resource> <verb> [flags...]
```

Apollo is a **sales-intelligence + engagement** platform. The tool wraps the
Apollo REST API and prints the provider's JSON on stdout verbatim, so you read
Apollo's own response shape (including its `pagination` block on list calls).

## The mental model

An agent works Apollo in this order:

1. **Find** prospects (`people search`) or target accounts (`org search`).
2. **Enrich** a known person or company to verified email/phone/firmographics
   (`people enrich` / `org enrich`) — this is the credit-consuming step.
3. **Save** a prospect as a contact (`contacts create`) — the prerequisite for
   sequencing.
4. **Engage**: enroll contacts into an outbound sequence (`sequences add`),
   create follow-up tasks (`tasks create`), and read/advance deals (`deals`).

Resource groups: `people`, `org`, `contacts`, `accounts`, `sequences`,
`tasks`, `deals`, `users`, `email-accounts`.

## Core commands

```bash
# Prospecting
heliox tool apollo -- people search --title "VP Sales" --seniority vp --location "United States" --per-page 25 --json
heliox tool apollo -- org search --industry saas --employees-min 50 --employees-max 500 --json

# Enrichment (consumes credits when contact data is revealed)
heliox tool apollo -- people enrich --email jane@acme.com --json
heliox tool apollo -- people enrich --name "Jane Doe" --org-domain acme.com --reveal-phone --json
heliox tool apollo -- org enrich --domain acme.com --json

# Contacts (persist a prospect so it can be sequenced)
heliox tool apollo -- contacts create --first-name Jane --last-name Doe --email jane@acme.com --title "VP Sales" --json
heliox tool apollo -- contacts search --q acme --json
heliox tool apollo -- contacts stages --json                       # stage ids for `contacts update --stage-id`
heliox tool apollo -- contacts update <contact_id> --stage-id <id> --json

# Sequences (outbound campaigns)
heliox tool apollo -- sequences list --json
heliox tool apollo -- email-accounts list --json                   # get a sending mailbox id first
heliox tool apollo -- sequences add <sequence_id> --contact-ids <id> --contact-ids <id> --email-account-id <mailbox_id> --json
heliox tool apollo -- sequences stop --sequence-id <id> --contact-ids <id> --mode remove_from_sequence --json

# Tasks and deals
heliox tool apollo -- tasks create --contact-id <id> --type call --priority high --due-at 2026-08-01T09:00:00Z --json
heliox tool apollo -- deals search --json
heliox tool apollo -- deals create --name "Acme expansion" --account-id <id> --amount 5000 --json
```

Every command accepts `--body '<json>'` — a raw JSON object merged as the
request body base, so you can pass any Apollo filter/field the typed flags do
not name (typed flags override). Run `-- <resource> <verb> --help` for the
exact flags rather than guessing.

## Footguns (where agents go wrong)

- **Search returns people WITHOUT contact details.** `people search` gives you
  matches and Apollo ids; the verified email/phone only comes from
  `people enrich` (which spends credits). Don't report "no email found" from a
  search result — enrich the person first.
- **Some endpoints require an Apollo master API key and reject your OAuth
  token with a 403.** Apollo documents `people search`, `sequences add`,
  `sequences stop`, `deals search`, and `deals update` as master-key-only. If
  you hit a 403 with a "may require an Apollo master API key" hint, that
  capability is not reachable with the connected OAuth account — do not retry in
  a loop; use the enrich/contacts/tasks path or tell the user.
- **Enrolling into a sequence needs a sending mailbox.** `sequences add` wants
  `--email-account-id`; get it from `email-accounts list` first. Without it the
  enrollment has no mailbox to send from.
- **Enrichment spends credits.** `people enrich --reveal-phone` /
  `--reveal-personal-emails` consume Apollo credits and phone reveals return
  asynchronously. Only reveal what the task needs.
- **`--account` when more than one Apollo account is connected.** A `409` lists
  the candidate account keys; re-run with `--account <key>` (before the `--`).

## Safety

- Sequencing and outbound tasks send email to real prospects — follow the
  sensitive-operation rule in [../SKILL.md](../SKILL.md) before enrolling
  contacts or creating outbound tasks.
- Enrichment and search consume the user's paid Apollo credits; don't run
  broad bulk enrichment without the user asking for it.
