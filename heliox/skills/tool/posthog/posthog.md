# PostHog (`heliox tool posthog -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. PostHog is a
**flat provider** (not grouped like `google`): everything after `--` is the
posthog tool's own CLI.

```bash
heliox tool posthog [--account <key>] -- <group> <verb> [flags...]
```

PostHog is product analytics: events, insights, dashboards, feature flags,
annotations, persons/cohorts, experiments, and ad-hoc HogQL queries.

The connection is a **personal API key** the user creates at Settings > Personal
API keys, not an OAuth grant — there is no auth link to relay. PostHog makes
them pick the key's scopes, and there is a trap worth stating when you ask for
one: besides the analytics scopes the commands below need, the key must also
carry **`user:read`**. Helio verifies the key against `/api/users/@me/` before
storing it, and a key scoped only to analytics is refused at connect with an
error that does not name the missing scope. Keys can also be limited to
specific projects or organizations; a key scoped to one project cannot reach
another.

## The mental model (read this first)

1. **Region.** PostHog Cloud is split into a US and an EU region, and a token is
   valid in exactly one of them. The tool resolves the region for you (probes US
   then EU) and prints it. You never pass a host. `whoami` shows the resolved
   region host. (Self-hosted instances are only reachable via the harness
   `POSTHOG_API_HOST` override, not a Helio connection.)

2. **Project id is required for almost everything.** Analytics data lives under a
   project. Discover the id first, then pass `--project <id>` to every data
   command:

   ```bash
   heliox tool posthog -- project list --json
   ```

3. **Passthrough JSON.** List commands return PostHog's
   `{"count","next","previous","results"}` envelope untouched; page with
   `--limit` / `--offset`. Errors surface PostHog's `{"type","code","detail"}`
   body verbatim.

## Core commands

### Orientation

```bash
heliox tool posthog -- whoami --json                 # user + resolved region host
heliox tool posthog -- project list --json           # discover --project ids
```

### Ad-hoc analytics (HogQL)

`query run` is the workhorse for "how did the launch do?" questions. Pass a
HogQL string, or a raw query node for advanced kinds (TrendsQuery, FunnelsQuery).

```bash
heliox tool posthog -- query run --project 1 \
  --hogql "select event, count() from events where timestamp > now() - interval 7 day group by event order by count() desc limit 20" --json

# advanced: a raw query node from a file (or - for stdin)
heliox tool posthog -- query run --project 1 --query-json ./trends.json --json
```

HogQL quick reference: `select ... from events`, filter on `timestamp`,
`event`, `properties.<key>`, `person.properties.<key>`; aggregate with
`count()`, `uniq(person_id)`, `avg(...)`; default 100 rows, `LIMIT` up to 50k;
this is for analysis, not bulk export.

### Insights & dashboards (read the team's saved work)

```bash
heliox tool posthog -- insight list --project 1 --search "activation" --json
heliox tool posthog -- insight get --project 1 --id <id> --json
heliox tool posthog -- dashboard list --project 1 --json
heliox tool posthog -- dashboard get --project 1 --id <id> --json
```

### Feature flags

```bash
heliox tool posthog -- flag list --project 1 --search "checkout" --json
heliox tool posthog -- flag get --project 1 --id <id> --json
heliox tool posthog -- flag toggle --project 1 --id <id> --active=true --json   # enable/disable
heliox tool posthog -- flag create --project 1 --data ./flag.json --json         # raw flag body
heliox tool posthog -- flag update --project 1 --id <id> --data ./patch.json --json
```

**Caution:** `flag toggle --active=true|false` flips a live flag for real users.
Confirm the flag id and direction before toggling; prefer `flag get` first.

### Annotations (mark deploys / launches on the timeline)

```bash
heliox tool posthog -- annotation list --project 1 --json
heliox tool posthog -- annotation create --project 1 \
  --content "Deployed v2.3" --date-marker "2026-07-22T00:00:00Z" --scope project --json
```

### People, cohorts, experiments, recordings, definitions

```bash
heliox tool posthog -- person list --project 1 --search "ada@example.com" --json
heliox tool posthog -- person get --project 1 --id <id> --json
heliox tool posthog -- cohort list --project 1 --json
heliox tool posthog -- experiment list --project 1 --json
heliox tool posthog -- experiment get --project 1 --id <id> --json
heliox tool posthog -- recording list --project 1 --json          # metadata only
heliox tool posthog -- event-definition list --project 1 --search "signup" --json     # HogQL authoring aid
heliox tool posthog -- property-definition list --project 1 --search "plan" --json
```

## Footguns

- **No `--project` → usage error (exit 2).** Run `project list` first; the id is
  the numeric/string project id, not its name.
- **`event-definition` / `property-definition` before writing HogQL.** If a query
  returns nothing, check the exact event and property names exist — these two
  lists are the source of truth for what you can `select` and filter on.
- **Rate limits are org-wide.** A `429` body is passed through verbatim (exit 1);
  do not retry in a loop — back off or narrow the query.
- **Write scope is small by design.** Only feature flags and annotations are
  writable; everything else is read-only. Insight/dashboard creation is not
  wrapped — use `query run` for ad-hoc analysis.
