# QuickBooks Online (`heliox tool quickbooks -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. QuickBooks is a
**flat provider** (not grouped like `google`): everything after `--` is the
quickbooks tool's own CLI.

```bash
heliox tool quickbooks [--account <realmId>] -- <resource> <verb> [flags...]
```

The tool wraps Intuit's **Accounting API v3** plus the **Reports API**. Every
call is scoped to one **company** (Intuit's `realmId`), captured at connect
time and used automatically: you never pass it in commands.

## The mental model (read this first)

- **`query` is the workhorse.** Most "list / find / how much / who" questions
  are one `query` call using QuickBooks' SQL-like grammar. Reach for the
  per-resource `list` only when you want the same read with simple flags.
- **Reads are cheap; writes take raw entity JSON.** `create` posts a QuickBooks
  entity object verbatim (`--json-body`), because QuickBooks models both create
  and update as a full/sparse upsert on the same `POST /{entity}`.
- **Amounts and references are QuickBooks-shaped.** A line item carries an
  `Amount`, a `DetailType`, and reference objects like
  `"CustomerRef": {"value": "<id>"}`. Fetch an example with `get` before writing.

## Core commands

### Read

```bash
# Company identity / health check
heliox tool quickbooks -- company get --json

# The query workhorse (QuickBooks SQL-like grammar)
heliox tool quickbooks -- query --sql "select * from Invoice where Balance > '0'" --json
heliox tool quickbooks -- query --sql "select * from Customer where Active = true" --json

# Per-resource list (thin wrapper over query) + get by id
heliox tool quickbooks -- invoice list --where "Balance > '0'" --max 20 --json
heliox tool quickbooks -- customer get --id 42 --json
heliox tool quickbooks -- bill list --json
heliox tool quickbooks -- vendor get --id 7 --json
heliox tool quickbooks -- account list --json
heliox tool quickbooks -- item list --json
heliox tool quickbooks -- payment list --json
```

Resources with `list`/`get`: `customer`, `invoice`, `bill`, `vendor`,
`payment`, `account`, `item`. Pagination is inside the query grammar
(`--start-position` = `STARTPOSITION`, `--max` = `MAXRESULTS`), not header
links.

### Reports

```bash
heliox tool quickbooks -- report get --name ProfitAndLoss --start-date 2024-01-01 --end-date 2024-12-31 --json
heliox tool quickbooks -- report get --name BalanceSheet --date-macro "This Fiscal Year" --json
heliox tool quickbooks -- report get --name AgedReceivables --json
```

Common report names: `ProfitAndLoss`, `BalanceSheet`, `AgedReceivables`,
`AgedPayables`, `CashFlow`, `GeneralLedger`. Extra report params:
`--param key=value` (repeatable).

### Write (create / upsert)

`customer`, `invoice`, `bill`, `vendor`, `payment` support `create --json-body`
with a raw QuickBooks entity object:

```bash
heliox tool quickbooks -- customer create --json-body '{"DisplayName":"Acme Ltd"}' --json

heliox tool quickbooks -- invoice create --json-body '{
  "CustomerRef": {"value": "42"},
  "Line": [{
    "Amount": 4000.00,
    "DetailType": "SalesItemLineDetail",
    "SalesItemLineDetail": {"ItemRef": {"value": "1"}}
  }]
}' --json

# Email an existing invoice (uses the invoice BillEmail if --to is omitted)
heliox tool quickbooks -- invoice send --id 7 --to cfo@acme.com --json
```

## Footguns

- **`realmId` is the account, not a flag.** One connection = one company. To
  work across companies, connect each and select with `--account <realmId>`.
- **Read a row before you write it.** Field names and reference shapes
  (`CustomerRef`, `ItemRef`, `AccountRef`) are exact: `get` a similar record
  first and mirror its structure in `--json-body`.
- **Errors carry the real reason.** A failed call surfaces QuickBooks' `Fault`
  array (code + detail), e.g. a `ValidationFault` on a bad `Line`. Under
  `--json` it lands in `error.fault`; read it rather than retrying blindly.
- **Payments/Payroll are out of scope.** This tool is Accounting + Reports
  only.
