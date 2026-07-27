# Omnisend (`heliox tool omnisend -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Omnisend is a
**flat provider** (not grouped like `google`): everything after `--` is the
omnisend tool's own CLI.

```bash
heliox tool omnisend [--account <key>] -- <resource> <verb> [flags...]
```

The tool wraps Omnisend's **dated API line** (`https://api.omnisend.com/api`,
`Omnisend-Version: 2026-03-15`) with the connected credential. Commands are
grouped by resource: `contact`, `event`, `campaign`, `segment`, `product`,
`batch`, `brand`.

**Omnisend is not connectable right now** — the provider is withheld from the
catalog while its credential form changes, so `heliox tool omnisend auth` has
nothing to offer. If a user asks for Omnisend, say it is unavailable rather
than walking them through a connect flow that cannot complete.

## The mental model

- **Reads** (`list`, `get`) are structured: they take flags and print the
  provider JSON verbatim on stdout.
- **Writes** (`create`, `update`, `event send`, `segment create`, `batch
  create`) take a single `--data '<json>'` body that is sent through
  unchanged. This means you control the exact Omnisend request schema — the
  tool never guesses nested shapes like a contact's `identifiers`/`channels`.

## Pagination

List responses carry `paging.cursors.after` (and `paging.hasMore`). To page,
pass that cursor back with `--after`:

```bash
heliox tool omnisend -- contact list --limit 100 --json
# read paging.cursors.after from the output, then:
heliox tool omnisend -- contact list --limit 100 --after "<cursor>" --json
```

## Core commands

### Audience (contacts)

```bash
heliox tool omnisend -- contact list [--email a@b.com] [--limit 50] [--after <cursor>] --json
heliox tool omnisend -- contact get --id <contactID> --json
# --data is the raw Omnisend contact body (identifiers + channels + fields):
heliox tool omnisend -- contact create --data '{"identifiers":[{"type":"email","id":"a@b.com","channels":{"email":{"status":"subscribed"}}}],"firstName":"Ada"}' --json
heliox tool omnisend -- contact update --id <contactID> --data '{"tags":["vip"]}' --json
```

### Trigger an automation (events)

```bash
# fire a custom event that starts an Omnisend workflow ("trial started", "renewed")
heliox tool omnisend -- event send --data '{"eventName":"trial started","contact":{"email":"a@b.com"},"properties":{"plan":"pro"}}' --json
```

### Campaigns (read)

```bash
heliox tool omnisend -- campaign list [--limit 25] [--after <cursor>] --json
heliox tool omnisend -- campaign get --id <campaignID> --json
```

### Segments and products

```bash
heliox tool omnisend -- segment list --json
heliox tool omnisend -- segment get --id <segmentID> --json
heliox tool omnisend -- segment create --data '{"name":"VIP buyers","filter":{...}}' --json
heliox tool omnisend -- product list [--limit 50] --json
heliox tool omnisend -- product get --id <productID> --json
```

### Bulk (batches) and account

```bash
heliox tool omnisend -- batch create --data '{"method":"POST","endpoint":"contacts","items":[...]}' --json
heliox tool omnisend -- batch get --id <batchID> --json
heliox tool omnisend -- brand get --json   # which store this connection is bound to
```

## Exit codes

- `0` success.
- `1` runtime/API failure (Omnisend non-2xx, transport). Under `--json`, stderr
  carries `{"error":{"message":…,"kind":"api","status":<n>}}`. A `401` also
  marks the connection's credential rejected.
- `2` usage error (missing required flag, malformed `--data` JSON, unknown
  subcommand) — nothing was sent to Omnisend.
