# Mercury (`heliox tool mercury -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Mercury is a
**flat provider** (not grouped like `google`): everything after `--` is the
mercury tool's own CLI. Mercury is a US business bank; this tool reads a
company's accounts, transactions, recipients (payees), treasury, and cards.

```bash
heliox tool mercury [--account <key>] -- <resource> <verb> [flags...]
```

> `--account` here is the **Helio connection** selector (which connected Mercury
> login), not a bank account. A Mercury *bank* account id is passed to the
> commands below via the `--account` flag **after** `--` (e.g.
> `transaction list --account <bankAccountId>`). They are different `--account`s
> at different layers.

## This tool is read-only

Money movement (send money, internal transfers, creating/editing recipients) is
**not** exposed. Every verb is a GET. Use it to answer "what's our balance",
"show last week's transactions", "who did we pay", "which cards are on this
account".

## Output shape (uniform)

All commands emit JSON to stdout:

- **list** verbs → `{ "data": [ ... ] }`, plus pagination metadata when the API
  returns it (`total` for transactions; `page` cursor for accounts / recipients
  / treasury).
- **get** verbs → `{ "data": { ... } }`.

The objects inside `data` are Mercury's own fields (already flat and
agent-friendly): e.g. an account has `id`, `name`, `nickname`, `status`,
`availableBalance`, `currentBalance`, `accountNumber`, `routingNumber`; a
transaction has `id`, `amount`, `status`, `kind`, `counterpartyName`,
`createdAt`, `postedAt`, `note`.

Errors print to stderr (add `--json` for a structured `{"error":{...}}`
envelope) and exit non-zero (`1` API/runtime, `2` bad usage).

## Verbs

```bash
# Accounts (the org's Mercury bank accounts)
mercury -- account list [--limit N] [--order asc|desc] [--start-after <id>] [--end-before <id>]
mercury -- account get <account-id>

# Transactions (scoped to one bank account; --account is REQUIRED)
mercury -- transaction list --account <account-id> \
        [--limit N] [--offset N] [--order asc|desc] \
        [--start YYYY-MM-DD] [--end YYYY-MM-DD] [--search <text>] \
        [--status pending|sent|cancelled|failed|reversed|blocked]
mercury -- transaction get <transaction-id> --account <account-id>

# Recipients (payees)
mercury -- recipient list [--limit N] [--start-after <id>] [--end-before <id>]
mercury -- recipient get <recipient-id>

# Treasury (money-market / T-bill accounts + yield)
mercury -- treasury get

# Cards on an account (--account REQUIRED)
mercury -- card list --account <account-id>
```

## Footguns

- **Get an account id first.** `transaction list`, `transaction get`, and
  `card list` all require `--account <bankAccountId>`. Start with
  `account list`, pick the id from `data[].id`, then pass it.
- **Accounts/recipients/treasury paginate by cursor, not offset.** Use
  `--start-after` / `--end-before` (an account/recipient id), not `--offset`.
  Only `transaction list` uses `--offset`.
- **Transactions default to the last 30 days.** Pass `--start` / `--end`
  (YYYY-MM-DD or ISO 8601) to widen the window.
- **Amounts are signed numbers.** A debit is negative, a credit positive; don't
  assume a separate direction field.
