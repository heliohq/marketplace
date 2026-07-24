# Amplitude (`heliox tool amplitude`)

Read/query access to a connected Amplitude project's product analytics. Start
from [../SKILL.md](../SKILL.md) for the connect/list/use model — this page is the
Amplitude command surface.

**Read-only, analysis tool.** Every command reads or queries results
(segmentation, funnels, retention, cohorts, user activity, saved charts, raw
export). There is no event-ingestion command by design — sending events is a
build-time SDK concern, and an assistant must never fabricate analytics events.

## Connecting

Amplitude authenticates with HTTP Basic auth using a project **API Key** and
**Secret Key** (both in Amplitude → project Settings → General). The user pastes
them as **one colon-joined value**:

```
apiKey:secretKey
```

Relay the `heliox tool amplitude auth` link and tell the user to paste that
combined value. No OAuth, no app registration.

## Region (US vs EU) — read this before you query

An Amplitude project lives in exactly **one** data-residency region. The keys of
an EU project are unknown to the US host and vice-versa. The tool defaults to
the **US** host and cannot tell the region from the credential.

- Default (no flag) → `https://amplitude.com` (US).
- `--region eu` → `https://analytics.eu.amplitude.com`.

If a default (US) call returns **401**, it may simply be an EU-project key hitting
the wrong host — the error says so. **Retry the same command with `--region eu`
before concluding the credential is dead.** Only a 401 on an explicitly chosen
region means reconnect. Put `--region eu` before the `--` (it is a tool flag):

```bash
heliox tool amplitude -- events list                 # US (default)
heliox tool amplitude --region eu -- events list     # EU project
```

## Commands

All arguments go after `--`. JSON responses are passed through verbatim.

| Command | Purpose |
| --- | --- |
| `events list` | Catalog of tracked event types — run this first to get valid event names |
| `segmentation --events '<json>' --start YYYYMMDD --end YYYYMMDD` | Event counts/uniques over time (the core metric query) |
| `funnels --events '<json>' --events '<json>' --start … --end …` | Conversion / drop-off across an ordered event list (≥2 `--events`, in order) |
| `retention --start-event '<json>' --returning-event '<json>' --start … --end …` | N-day / bracket retention |
| `user-search --user <id-or-email>` | Resolve a user / device / email → Amplitude ID |
| `user-activity --user <amplitude-id>` | A user's raw event stream (use the id from `user-search`) |
| `chart --id <chart-id>` | Results behind an existing saved chart (returned as a CSV JSON envelope) |
| `cohorts list` | Discoverable behavioral cohorts (metadata) |
| `export --start YYYYMMDDTHH --end YYYYMMDDTHH [--output path]` | Raw event export (zip); streamed to a file, a JSON receipt is printed |

Dates are `YYYYMMDD` (`export` uses hour granularity `YYYYMMDDTHH`).

### Event / segment grammar (`--events` / `--segment`)

Amplitude's event and segment definitions are large JSON grammars, so they pass
through as **raw JSON strings** — the tool does not model them. The minimum is an
event object with `event_type`. Optional `--metric` (`uniques`|`totals`|…,
default `uniques`), `--interval` (`1`|`7`|`30`), `--segment` (user-property
filters as JSON), and `--group-by`.

One worked segmentation query (weekly totals of "Add to Cart" for January,
US-only):

```bash
heliox tool amplitude -- segmentation \
  --events '{"event_type":"Add to Cart"}' \
  --start 20260101 --end 20260131 \
  --metric totals --interval 7 \
  --segment '[{"prop":"country","op":"is","values":["United States"]}]'
```

Funnels take one `--events` per step, in order; retention uses `--start-event`
and `--returning-event` (not `--events`).

## Pacing (rate / query cost)

Amplitude's Dashboard REST API is cost-limited: roughly **1000 concurrent cost
units per 5 minutes** and **108,000 cost units/hour**, and heavy funnel/retention
queries over long ranges are expensive. Pace multi-query analyses — don't fan out
many wide-range funnel/retention calls at once, and prefer `events list` +
targeted date ranges over blind broad pulls. A `429` means slow down.

## Safety

Read-only, but analytics data is sensitive: `user-activity` and `export` expose
individual user event streams. Treat exported files and per-user data as
confidential — summarize, don't dump raw PII into a channel. Never echo the
`apiKey:secretKey` credential.
