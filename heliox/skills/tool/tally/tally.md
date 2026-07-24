# Tally (`heliox tool tally -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Tally is a
**flat provider** (not grouped like `google`): everything after `--` is the
tally tool's own CLI. Tally (tally.so) is a form builder; the load-bearing use
case is **reading the responses people submitted to a form**.

```bash
heliox tool tally [--account <key>] -- <resource> <verb> [flags...]
```

Connect is a **personal API key** (not OAuth): the user creates a key at
Settings → API keys (tally.so/settings/api-keys) and pastes it into the connect
link — `heliox tool tally auth --json` mints that link. The key is user-scoped
(inherits the creating user's access across their workspaces).

Every read command prints Tally's JSON response verbatim. List endpoints return
`{ "items": [...], "page", "limit", "total", "hasMore" }` — drive paging
yourself with `--page` / `--limit`; commands never auto-follow pagination.

## Core commands

### Read (the bread and butter)

```bash
# who am I (identity / workspaces sanity check)
heliox tool tally -- me

# list forms (optionally scope to workspaces; --workspace is repeatable)
heliox tool tally -- form list [--workspace <id>] [--page N] [--limit N]
heliox tool tally -- form get       --form <id>
heliox tool tally -- form questions --form <id>

# READ SUBMISSIONS — the main job
heliox tool tally -- submission list --form <id> \
    [--filter all|completed|partial] [--page N] [--limit N] \
    [--after-id <id>] [--start-date <iso>] [--end-date <iso>]
heliox tool tally -- submission get  --form <id> --submission <id>

# analytics: metric is a subcommand; --period is REQUIRED
heliox tool tally -- analytics metrics     --form <id> --period 30d
heliox tool tally -- analytics visits      --form <id> --period 7d
heliox tool tally -- analytics submissions --form <id> --period all
heliox tool tally -- analytics drop-off    --form <id> --period 24h
heliox tool tally -- analytics dimensions  --form <id> --period 12m

# workspaces
heliox tool tally -- workspace list [--page N]
```

`--period` accepts one of: `today yesterday 24h 7d 30d 3m 6m 12m all`.

### Write (secondary — forms and webhooks)

```bash
# create/update take a JSON body via --file <path> or --stdin (raw passthrough)
heliox tool tally -- form create --file new-form.json
heliox tool tally -- form update --form <id> --stdin < patch.json
heliox tool tally -- form delete --form <id>

heliox tool tally -- webhook list [--page N] [--limit N]
heliox tool tally -- webhook create --file hook.json
heliox tool tally -- webhook update --webhook <id> --stdin < patch.json
heliox tool tally -- webhook delete --webhook <id>
```

Run `-- <resource> --help` (or `-- <resource> <verb> --help`) for the exact
flags rather than guessing.

## Footguns

- **`analytics` requires `--period`.** Every analytics metric endpoint rejects a
  request with no `period`; the CLI enforces it (exit 2, no HTTP call). Pick a
  window from the enum above.
- **Paging is manual.** `submission list` / `form list` return one page. When
  `hasMore` is true, advance with `--page` (or pass `--after-id` for the
  submission cursor); the tool never sweeps all pages for you.
- **Rate limit is 100 req/min.** Prefer one wide `submission list` page over
  many `submission get` calls; Tally's own docs recommend webhooks over polling
  for high-volume intake.
- **`--file`/`--stdin` bodies are raw JSON passthrough.** The CLI validates the
  bytes are JSON and forwards them unchanged; a bad shape surfaces as Tally's
  own `4xx` (rendered as `{"error":{...,"status":<http>}}` under `--json`).
- **A stale/removed key stops working.** The key is tied to the creating user;
  if they leave the org, a `401 reconnect required` means ask for a fresh key.
- **`--account` when more than one Tally account is connected.** A `409` lists
  the candidate account keys; re-run with `--account <key>` before the `--`.

## Safety

- Creating or deleting forms and webhooks changes what the user's respondents
  see and where their data is sent — outward-facing. Follow the
  sensitive-operation rule in [../SKILL.md](../SKILL.md) and confirm before a
  `form delete` or `webhook create/delete` against anything you did not create.
- Submission bodies are respondent PII; never echo raw submissions into public
  channels without the user's intent.
