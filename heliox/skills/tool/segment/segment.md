# Segment (`heliox tool segment -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Segment is a
**flat provider** (not grouped like `google`): everything after `--` is the
segment tool's own CLI.

```bash
heliox tool segment [--account <key>] -- <resource> <verb> [flags...]
```

This wraps the **Segment (Twilio) Public API** — the workspace management &
observability plane (`https://api.segmentapis.com`). It is **read-first**: you
inspect wiring, delivery health, tracking plans, and admin, but do not emit
analytics events (the Tracking API / write keys are out of scope). Auth is a
workspace-scoped Public API token connected by the user; the tool injects the
`Authorization: Bearer` header for you.

Every command prints the provider JSON **verbatim** on stdout (the Segment
`{"data": …, "pagination": …}` envelope, unchanged), so you can page and parse
without the tool reshaping anything.

## The mental model

- One connected account == one **Segment workspace** (Public API tokens are
  workspace-scoped). `--account` picks between multiple.
- A **source** ingests events; a **destination** receives them; a **warehouse**
  is a SQL sink. `source connected-destinations` shows the wiring between them.
- **Access is Team/Business-tier** — the Public API is not available on free
  workspaces. Data residency is **US-only in v1** (an EU workspace token will
  fail; that is a known limitation, not a bug you can fix).

## Core commands

### Inventory & wiring

```bash
heliox tool segment -- workspace get                              # the connected workspace (identity)
heliox tool segment -- source list --count 100                   # sources (paginate with --cursor)
heliox tool segment -- source get --id <sourceId>
heliox tool segment -- source connected-destinations --id <sourceId>
heliox tool segment -- destination list
heliox tool segment -- destination get --id <destinationId>
heliox tool segment -- warehouse list
heliox tool segment -- warehouse get --id <warehouseId>
```

### Observability (the highest-value use)

```bash
# whole-workspace event volume over time (workspace-scoped)
heliox tool segment -- delivery events-volume --granularity HOUR \
  --start 2026-07-01T00:00:00Z --end 2026-07-02T00:00:00Z

# delivery metrics summary for one destination (destination-scoped)
heliox tool segment -- delivery metrics --destination-id <destinationId> \
  --param sourceId=<sourceId>
```

### Governance & admin

```bash
heliox tool segment -- tracking-plan list
heliox tool segment -- tracking-plan get --id <trackingPlanId>
heliox tool segment -- tracking-plan rules --id <trackingPlanId>
heliox tool segment -- function list
heliox tool segment -- space list                                # Unify spaces
heliox tool segment -- space audiences --id <spaceId>
heliox tool segment -- iam user list
heliox tool segment -- iam group list
```

### Raw escape hatch

The Public API has 100+ endpoints; anything without a first-class command is
reachable through `request` (bearer-injected, JSON passed through). Writes are
possible here only with an explicit non-GET `--method` — treat any non-GET as a
sensitive operation and confirm with the user first.

```bash
heliox tool segment -- request --method GET --path /sources --query pagination.count=5
heliox tool segment -- request --method GET --path /warehouses/<id>
```

## Pagination

List commands take `--count` (1–1000; Segment defaults to 200) and `--cursor`.
Read the next cursor from the response's `pagination.next` and pass it back as
`--cursor` to get the following page. There is no auto-follow flag — page
explicitly.

## Footguns

- **Read-first.** No dedicated create/update/delete commands ship. Mutations
  are only reachable via `request --method POST|PATCH|DELETE` — a sensitive
  action against a production CDP; confirm first.
- **IAM paths are `/users` and `/groups`.** The `iam` grouping is a CLI/UX
  convenience; if you hand-write a raw `request --path`, use `/users` and
  `/groups`, not `/iam/users`.
- **Tier + region.** A 401/403 on every call usually means the workspace lacks
  Public API access (not Team/Business) or is EU-resident (v1 targets US only) —
  not a transient error to retry.
