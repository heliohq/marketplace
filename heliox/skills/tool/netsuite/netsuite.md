# NetSuite (`heliox tool netsuite -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. NetSuite is a
**flat provider** (not grouped): everything after `--` is the netsuite tool's
own CLI. It wraps Oracle NetSuite's **SuiteTalk REST Web Services** (record
CRUD, SuiteQL queries, and the metadata catalog) authenticated with the user's
Token-Based Authentication (TBA) credentials, which Helio injects per call.

```bash
heliox tool netsuite [--account <key>] -- <command> [flags...]
```

## The mental model (read this first)

NetSuite has two complementary read paths, and one write path:

- **SuiteQL (`query`)** is the workhorse for **answering questions**: joined,
  aggregated reads across records ("what did we invoice ACME last quarter",
  "open sales orders by rep"). Prefer it whenever you need more than one record
  or any join/filter/aggregate.
- **Record get/list (`record get` / `record list`)** fetch a **specific record**
  by internal id, or list ids of a type.
- **Record create/update/delete** mutate a single record. These are
  side-effecting; treat them carefully.

Use `metadata` first when you don't know a record type's exact name or fields.

## Core commands

### Query (SuiteQL, the primary read path)

```bash
# Joined / aggregate reads. --limit / --offset paginate.
heliox tool netsuite -- query --q "SELECT id, companyName, email FROM customer FETCH FIRST 20 ROWS ONLY" --json
heliox tool netsuite -- query --q "SELECT tranId, total FROM transaction WHERE type='SalesOrd'" --limit 50 --offset 50 --json
```

The response carries `items`, plus `hasMore`, `count`, `totalResults`, and
`links` (the `rel:next` link signals another page). SuiteQL is SELECT-only.

### Records

```bash
# Discover types/fields first when unsure
heliox tool netsuite -- metadata --json                 # full catalog
heliox tool netsuite -- metadata --type customer --json # one record type's schema

# Read
heliox tool netsuite -- record get  --type customer --id 1234 --json
heliox tool netsuite -- record list --type customer --limit 20 --json

# Write (side-effecting)
heliox tool netsuite -- record create --type customer --body '{"companyName":"ACME","subsidiary":{"id":"1"}}' --json
heliox tool netsuite -- record update --type customer --id 1234 --body '{"comments":"VIP"}' --json
heliox tool netsuite -- record delete --type customer --id 1234 --json
```

`record create` returns the new internal id (`{"id":"...","location":"..."}`)
surfaced from NetSuite's `Location` header. `record update` is a PATCH: send
only the fields you are changing.

## Output and errors

Every command takes `--json` (structured); prefer it. The exit-code contract:
**0** success, **1** runtime/API failure (NetSuite non-2xx, including `401`
credential rejection and `429` governance throttling, or a transport error),
**2** usage/parse error (missing/invalid flags, bad `--body` JSON).

Under `--json`, errors render as `{"error":{"message":...,"kind":"usage|api",
"status":<HTTP>,"retry_after":<seconds>}}`. On a `429`, `retry_after` is set
only when NetSuite actually returns a `Retry-After` header. Back off and retry
later rather than hammering; the tool never blocks or auto-retries for you.

## Footguns

- **SuiteQL is SELECT-only.** To change data, use `record create/update/delete`,
  not `query`.
- **Record type names are exact and case-sensitive** (`salesOrder`, `customer`,
  `invoice`, `vendorBill`, …). If a type is rejected, check `metadata`.
- **Governance (429) is per-account.** Large scans can trip the concurrency
  limit; page with `--limit`/`--offset` and space out heavy queries.
- **Connect is credential-entry, not OAuth.** The user pastes a JSON object with
  their `account_id` and the four TBA secrets (`consumer_key`,
  `consumer_secret`, `token_id`, `token_secret`) generated inside their own
  NetSuite account. There is no consent screen. If nothing is connected,
  `heliox tool list` shows no netsuite row; ask the user to connect first.
