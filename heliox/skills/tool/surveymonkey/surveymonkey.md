# SurveyMonkey (`heliox tool surveymonkey -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. SurveyMonkey is
a **flat provider** (not grouped like `google`): everything after `--` is the
surveymonkey tool's own CLI.

```bash
heliox tool surveymonkey [--account <key>] -- <resource> <verb> [flags...]
```

The tool is **read-only**: it discovers surveys, reads their structure, reads
responses, lists collectors, and returns the connected user's identity. Output
is SurveyMonkey's own JSON, passed through verbatim (list endpoints return the
`{ "data": [...], "page", "per_page", "total", "links": {...} }` envelope: page
with `--page`/`--per-page`).

## The mental model (read this first)

Analyzing a survey is a chain: **find the survey → read its structure → read the
responses → interpret answers against the structure.**

- `survey list` / `survey get` find a survey and its `response_count`.
- `survey details` returns the **question + answer-option ids**: the map you
  need to make sense of answer ids in responses.
- `response list` returns response **metadata only** (ids/hrefs, filterable by
  status/date): enough to *count* completed vs partial, but **no answers**.
- `response bulk` / `response get` return the actual **answers** (selected
  choice ids), which you interpret using `survey details`.

## Core commands

```bash
# identity of the connected account (team, plan)
heliox tool surveymonkey -- me --json

# discover surveys (paginated)
heliox tool surveymonkey -- survey list --page 1 --per-page 50 --json
heliox tool surveymonkey -- survey get --id <survey-id> --json         # metadata incl. response_count
heliox tool surveymonkey -- survey details --id <survey-id> --json     # pages/questions/answer-option ids

# responses
heliox tool surveymonkey -- response list --survey <id> --status completed --json   # metadata list (no answers)
heliox tool surveymonkey -- response bulk --survey <id> --status completed --json   # full answers (PAID scope)
heliox tool surveymonkey -- response get  --survey <id> --id <response-id> --json    # one full response (PAID scope)

# collectors that gathered a survey's responses
heliox tool surveymonkey -- collector list --survey <id> --json

# generic read escape hatch for any v3 GET endpoint not modeled above
heliox tool surveymonkey -- fetch --path surveys/<id>/rollups --json
```

`response list` / `response bulk` accept `--status` (completed, partial,
overquota, disqualified) and date filters (`--start-modified-at`,
`--end-modified-at`, `--start-created-at`, `--end-created-at`), plus
`--page`/`--per-page`. Run `-- <resource> <verb> --help` for exact flags.

## Footguns (where agents go wrong)

- **Reading survey answers needs a PAID SurveyMonkey plan.** `response bulk` and
  `response get` are the only commands that return actual answers, and they
  require the paid `responses_read_detail` permission. On a free-plan connection
  they fail with a clear **"reading survey answers requires a paid SurveyMonkey
  plan"** message (SurveyMonkey codes 1014/1015). This is a plan limitation, not
  a bug: do not retry, and do not try to reach answers another way. Tell the
  user their SurveyMonkey account must be on a paid plan to read answers.
- **Counts and structure work on a free plan.** If answers are paywalled you can
  still deliver a lot: `survey get` gives `response_count`; `response list`
  (metadata only) paginates response ids and its envelope `total` gives filtered
  counts (e.g. `--status completed`); `survey details` gives the full question
  structure; `collector list` lists collectors. Reach for these before telling
  the user you're blocked.
- **Answer ids are meaningless without `survey details`.** A response's answers
  reference question ids and answer-option ids, not human text. Fetch
  `survey details` for the survey and map the ids before summarizing results.
- **`response list` has no answers by design.** It is the free, metadata-only
  list (ids/hrefs). If you need what people actually answered, use
  `response bulk` / `response get` (paid).
- **Region cap.** A SurveyMonkey account served from a non-default datacenter
  (e.g. EU data residency) is not supported here and fails with a "region not
  supported" message (code 1018). Report it to the user; there is no workaround
  in this integration.
- **Rate limits.** SurveyMonkey enforces per-minute and per-day app limits; a
  `429` (code 1040) means retry after the reset window, not a bad request.
- **`--account` when more than one SurveyMonkey account is connected.** A `409`
  lists the candidate account keys; re-run with `--account <key>` before the `--`.

## Safety

- This tool is read-only: it cannot create, edit, or delete surveys or
  responses. Survey response data is often personal/sensitive; handle it per the
  sensitive-data guidance in [../SKILL.md](../SKILL.md) and don't echo raw
  respondent contents into shared channels without the user's intent.
