# Brex (`heliox tool brex -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Brex is a
**flat provider** (not grouped like `google`): everything after `--` is the
brex tool's own CLI.

```bash
heliox tool brex [--account <key>] -- <resource> <verb> [flags...]
```

Brex connects you to a customer's **Brex account** as a finance / spend-ops
colleague. The tool is **read-mostly**: it answers "what did we spend, on which
cards, by whom, against which budget", reconciles expenses, and reports
balances. It does not issue cards, move money, or run onboarding.

## The mental model

Commands are grouped by resource; each verb is a `GET` against `api.brex.com`
and prints the provider's JSON response verbatim. Every response is JSON, so
add `--json` is unnecessary for output shape (it only changes error rendering).

- `account` — card and cash balances
- `transaction` — the card / cash spend ledger
- `expense` — expenses and receipts (read)
- `card` — issued cards, limits, status
- `user` — who spent / cardholder lookup (Team API)
- `budget` — budgets, spend limits
- `department` / `location` — dimension lookups for grouping spend
- top-level `get <path>` — raw GET escape hatch for endpoints without a verb

## Core commands

```bash
# Balances
heliox tool brex -- account card                 # card account balances
heliox tool brex -- account cash                 # list cash accounts
heliox tool brex -- account cash <id>            # one cash account

# Spend ledger (paginated — see Pagination)
heliox tool brex -- transaction card-primary --limit 20
heliox tool brex -- transaction cash <cash-account-id> --limit 20

# Expenses
heliox tool brex -- expense list --limit 20      # all expenses
heliox tool brex -- expense card --limit 20      # card expenses
heliox tool brex -- expense get <expense-id>

# Cards
heliox tool brex -- card list --limit 20
heliox tool brex -- card get <card-id>

# Users / cardholders
heliox tool brex -- user list --limit 20
heliox tool brex -- user me                      # the authenticated user
heliox tool brex -- user get <user-id>

# Budgets
heliox tool brex -- budget list --limit 20
heliox tool brex -- budget get <budget-id>
heliox tool brex -- budget spend-limits --limit 20

# Dimensions
heliox tool brex -- department list
heliox tool brex -- location list

# Raw GET for the long tail
heliox tool brex -- get /v2/cards --param status=ACTIVE
```

## Pagination

List commands are cursor-paginated over Brex's `{ "items": [...],
"next_cursor": "..." }` envelope:

- `--limit <n>` — max items per page.
- `--cursor <c>` — resume from a prior response's `next_cursor`.
- `--all` — follow `next_cursor` to the end and return one merged
  `{ items, next_cursor: null }` envelope. Use it deliberately on large
  ledgers; prefer `--limit` for a quick look.

Without `--all`, the first page is returned verbatim (with its `next_cursor`
intact) so you can page manually.

## Exit codes

- `0` — success.
- `1` — a Brex API error (non-2xx; the message and HTTP status are on stderr)
  or a transport failure. A `401` means the token was rejected; the connection
  usually needs to be reconnected by the user.
- `2` — a usage error (missing argument, unknown subcommand, bad flag).

## Footguns

- **Read-only.** There are no write verbs (update memo, create budget, …) yet.
  If the user asks to change something in Brex, tell them it is not supported
  and stop — do not reach for `get` to fake a write; it only does `GET`.
- **`user me` is your identity anchor.** When you need the connected user's own
  id (e.g. to filter their spend), read it from `user me` rather than guessing.
- **Amounts are minor units.** Brex returns money as integer minor units with a
  currency code (e.g. `{ "amount": 12345, "currency": "USD" }` = $123.45).
  Convert before reporting a dollar figure.
