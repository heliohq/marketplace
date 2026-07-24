# Mixpanel (`heliox tool mixpanel -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Mixpanel is a
**flat provider** (not grouped like `google`): everything after `--` is the
mixpanel tool's own CLI.

```bash
heliox tool mixpanel [--account <project_id>] -- <verb> [flags...]
```

This is a **read-only product-analytics** tool over Mixpanel's Query, Lexicon
Schemas, Raw Data Export, and App APIs. Use it to answer questions like "how did
signups trend last week", "what's the activation funnel conversion", "which
events fire most", or "pull the retention curve for the mobile cohort". It does
**not** ingest events — that is the app's own instrumentation job on a different
credential.

## Connection is by project, not per call

The connected credential is a Mixpanel **Service Account** scoped to one
**project** in one **region** (us / eu / in). `project_id` and `region` are
captured at connect time and injected on every call — you never pass them.
`--account` selects among multiple connected Mixpanel projects (the account key
is the `project_id`); a `409` lists the candidates.

## Verbs

| Command | What it returns |
| --- | --- |
| `mixpanel me` | Runtime identity/auth probe — run right after connecting to confirm the credential works. |
| `mixpanel events-names` | **Primary event-name discovery** — the event names actively firing. Use this to learn what events exist. |
| `mixpanel segmentation --event <e> --from <YYYY-MM-DD> --to <YYYY-MM-DD>` | An event segmented over time (`--on`, `--where`, `--type general\|unique\|average`, `--unit`). |
| `mixpanel events --event <e> [--event <e2>] ...` | Event totals over time (`--type`, `--unit`, `--interval` or `--from`/`--to`). |
| `mixpanel funnels list` | Saved funnels (id + name). |
| `mixpanel funnels run --funnel-id <id>` | Run a saved funnel (`--from`, `--to`, `--on`, `--where`). |
| `mixpanel retention --from <d> --to <d>` | Cohort retention (`--born-event`, `--event`, `--retention-type`, `--interval`, `--unit`). |
| `mixpanel retention-frequency --from <d> --to <d>` | The frequency ("addiction") view. |
| `mixpanel insights --bookmark-id <id>` | Fetch a saved Insights report. |
| `mixpanel cohorts list` | Saved cohorts (id + name). |
| `mixpanel engage [--where <expr>] [--output-properties <p> ...] [--page <n>]` | Query People / user profiles. |
| `mixpanel lexicon list` | Authored Lexicon schemas only — a documentation overlay, **not** discovery (see below). |
| `mixpanel export --from <d> --to <d>` | Bounded raw event export as JSONL (`--event`, `--where`, `--limit`). |

For the full flag set on any verb, run `heliox tool mixpanel -- <verb> --help`.

## Footguns (read these — they prevent wrong conclusions)

- **Discover events with `events-names`, never with `lexicon`.** The Lexicon
  Schemas API returns **only** events/properties that have an *authored schema*
  — it is explicitly "a subset of the data that appears in Lexicon," and events
  fired in the last 30 days without a schema are omitted. A project that never
  authored schemas returns a **partial or empty** `lexicon list` even while
  events are actively firing. So **never read an empty or short `lexicon list`
  as "this project has no events"** — run `events-names` for the authoritative
  list; `lexicon` only supplements it with descriptions where authors created
  schemas.

- **Query API rate limits: 60 queries/hour, max 5 concurrent.** Firing many
  analytics calls in a row hits this readily. On a `429` / `rateLimit` error the
  envelope carries `retry_after_seconds` when Mixpanel provides one — **back off
  and retry** (wait the indicated seconds), do not retry immediately and do not
  give up. This is a transient signal, not a dead call.

- **`export` is line-delimited JSONL and unbounded by default.** That is why
  `--from`/`--to` are required. Keep the window tight and prefer `--event` /
  `--where` / `--limit` — a wide window can stream a very large volume.

- **A wrong or expired secret shows up as a distinct `401` credential error**
  (there is no connect-time verification for this provider). If `me` or any call
  returns a credential error, ask the user to disconnect and reconnect with a
  correct Service Account secret.

## Safety

This tool only reads analytics; there are no outward-facing actions. Never echo
the credential payload — the CLI never shows it to you.
