# Ramp (`heliox tool ramp -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Ramp is a
**flat provider** (not grouped like `google`): everything after `--` is the
ramp tool's own CLI.

```bash
heliox tool ramp [--account <key>] -- <resource> <verb> [flags...]
```

Ramp is your connected business's **finance / spend-ops** view over the Ramp
Developer API (`api.ramp.com/developer/v1`). This tool is **read-only**: it
answers "what did we spend, on which cards, by whom, in which
department/location" and reconciles card transactions and reimbursements. It
does **not** issue cards, move money, or approve anything.

## Resources (all read)

| Command | What it returns |
|---|---|
| `transaction list` / `transaction get <id>` | Card transaction ledger (the core "what did we spend"). |
| `reimbursement list` / `reimbursement get <id>` | Out-of-pocket reimbursements. |
| `card virtual [id]` / `card physical [id]` | Issued virtual or physical cards: list, or one by id. Ramp has no combined `/cards` list. |
| `user list` / `user get <id>` | Users and cardholders (who spent). |
| `department list` / `department get <id>` | Department dimension for grouping spend. |
| `location list` / `location get <id>` | Location dimension for grouping spend. |
| `business info` / `business balance` | Connected-business identity/entity, and its balance. |
| `get <path>` | Raw `GET /developer/v1/<path>` passthrough for read endpoints without a first-class verb. |

## Core commands

```bash
# who + what + where
heliox tool ramp -- business info --json
heliox tool ramp -- user list --json
heliox tool ramp -- transaction list --limit 25 --json

# one object by id
heliox tool ramp -- transaction get <transaction-id> --json
heliox tool ramp -- card virtual <card-id> --json

# raw passthrough (relative path only; host + token are injected)
heliox tool ramp -- get /developer/v1/transactions --param state=CLEARED --json
```

## Pagination

Ramp lists return a `{ "data": [...], "page": { "next": <url|null> } }`
envelope. Flags:

- `--limit <n>` → Ramp's `page_size`.
- `--cursor <start>` → resume from a prior response's `start` cursor.
- `--all` → follow `page.next` to the end and return one merged `data` array
  (`page.next` becomes `null`). Without `--all`, the first page is returned
  verbatim so you can follow `page.next` yourself.

## Conventions

- `--json` emits the provider envelope verbatim (and, on failure, a structured
  `{"error":{message,kind,status}}` envelope).
- Exit codes: `0` success, `1` runtime/API failure (Ramp non-2xx), `2`
  usage/parse error (bad flag, missing id, unknown subcommand).
- Every call sends the connection's OAuth bearer token; a `401` triggers the
  token gateway's refresh-and-retry automatically.

For anything not listed above, `heliox tool ramp -- --help` (and
`... <resource> --help`) is the reference.
