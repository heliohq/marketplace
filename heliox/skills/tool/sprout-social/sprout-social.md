# Sprout Social (`heliox tool sprout-social -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Sprout Social
is a **flat provider** (not grouped like `google`): everything after `--` is
the sprout-social tool's own CLI. Auth is one account-scoped API Access Token
the user pastes at connect time; you never handle it.

```bash
heliox tool sprout-social [--customer-id <id>] -- <group> <verb> [flags...] [--json]
```

## The mental model (read this first)

- **Customer id is pre-injected.** Almost every Sprout path is
  `/v1/{customer_id}/...`. The connected account's default customer id is
  already in your environment, so `heliox tool sprout-social -- analytics posts
  ...` just works: no discovery round-trip. A token that can see multiple
  customers: list them with `metadata client`, then target another with the
  global `--customer-id <id>` flag.
- **The filter endpoints speak Sprout's filter DSL, not flags.** Analytics,
  inbox messages, and cases are `POST`-with-a-query-body endpoints. Pass DSL
  clauses with repeatable `--filter`, e.g.
  `--filter "created_time.in(2026-01-01...2026-02-01)"` and
  `--filter "customer_profile_id.eq(1,2)"`. For anything the flags don't cover,
  send the whole query verbatim with `--body '<json>'` (it replaces the
  assembled body). Operators: `eq/neq`, `gt/gte/lt/lte`, `in` (`..` inclusive /
  `...` exclusive end), `exists`, `match`.
- **Publishing is draft-only.** The public API creates drafts (`is_draft` is
  always true); scheduling/approval happen in the Sprout app. You cannot publish
  live from here.
- **Output is the raw Sprout envelope** `{ "data": ..., "paging"?: ... }`,
  passed through so you can read every field and page. Analytics use index
  paging (`--page` / `paging.total_pages`); messages and cases use cursor paging
  (`--page-cursor` / `paging.next_cursor`). `--json` is accepted for uniformity.

## Command surface

```bash
# Discovery / ids
heliox tool sprout-social -- metadata client                 # customers this token can see (no cid)
heliox tool sprout-social -- metadata profiles               # social profiles for the customer
heliox tool sprout-social -- metadata tags|groups|users|topics|teams|queues

# Analytics (POST filter body; --metric repeatable; index paging)
heliox tool sprout-social -- analytics profiles --filter "..." --metric impressions --page 1
heliox tool sprout-social -- analytics posts --filter "..." --metric reactions --fields text --limit 50

# Inbox + cases (cursor paging)
heliox tool sprout-social -- messages list --filter "created_time.in(2026-01-01...2026-01-02)" --page-cursor <c>
heliox tool sprout-social -- cases filter --filter "case_id.eq(5)"

# Publishing (draft only)
heliox tool sprout-social -- publishing create --group-id <g> --profile-id <p> --profile-id <p2> --text "..."
heliox tool sprout-social -- publishing get <publishing_post_id>
```

Shared filter flags on analytics / messages / cases: `--filter` (repeatable),
`--fields` (comma-separated), `--sort` (repeatable), `--timezone`, and `--body`
(raw JSON, overrides the flags). `--metric` + `--page` are analytics-only;
`--page-cursor` is messages/cases-only.

## Footguns

- **A bare group shows help, not an error.** `metadata` alone prints help; give
  it a verb (`metadata profiles`).
- **`analytics`/`messages`/`cases` require `filters`.** Sprout returns a `400`
  (passed through) if you send none: always give at least one `--filter` or a
  `--body`.
- **Rate limits: 60 req/min, 250k/month.** Prefer one wide filtered query with
  paging over many small calls.
- **Exit codes:** `0` success, `1` Sprout/API failure (the envelope's `error`
  and the `X-Sprout-Request-ID` surface on stderr), `2` usage/parse error
  (missing customer id, bad `--body` JSON, missing required flags).
