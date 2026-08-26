# PhantomBuster (`heliox tool phantombuster -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. PhantomBuster
is a **flat provider** (not grouped): everything after `--` is the phantombuster
tool's own CLI.

```bash
heliox tool phantombuster [--account <key>] -- <resource> <verb> [flags...]
```

PhantomBuster runs cloud automations called **Phantoms** (LinkedIn/social/web
scraping, lead extraction, enrichment, outreach). It connects with a
**workspace API key**, not OAuth. That key grants **full access to the whole
workspace** (every Phantom, every result, billing/usage). Treat it as a
high-blast-radius credential and never echo it.

## The mental model (read this first)

A run is **asynchronous**. `agent launch` does not return a result. It queues a
**container** (one execution) and returns a `container_id`. You then **poll**
until the run reaches a terminal state, and **fetch the result** separately:

```
agent launch ──▶ container_id
                    │
        poll ◀──────┤  container get / agent output   (until data.is_running = false)
                    │
        result ◀────┘  container result                (the extracted rows)
```

Every command prints a provider-neutral envelope:

- success → `{ "ok": true, "data": { ... } }`
- failure → `{ "ok": false, "error": { "code": "api|usage", "status": <http?>, "message": "..." } }`

The raw PhantomBuster object is preserved under `data`; convenience fields are
added alongside it: `data.is_running` (poll-loop stop signal), `data.output_pos`
(the cursor to pass back as `--from-pos`), and `<field>_iso` mirrors of the
millisecond timestamps.

## Check quota BEFORE launching (the #1 footgun)

A launch that runs past the workspace's execution-time quota fails **mid-run**
with a `429` and **no recoverable partial result**: you lose the whole run.
Check remaining budget first:

```bash
heliox tool phantombuster -- org resources
```

## Core commands

### Discover

```bash
heliox tool phantombuster -- agent list                       # all Phantoms in the workspace
heliox tool phantombuster -- agent list --input-types linkedin
heliox tool phantombuster -- agent get --id <agentId>         # one Phantom (carries s3Folder for result URLs)
heliox tool phantombuster -- org get                          # workspace identity
heliox tool phantombuster -- me                               # current user
```

### Launch → poll → result

```bash
# 1. Launch (optionally override the argument JSON; --save-argument persists it as the default)
heliox tool phantombuster -- agent launch --id <agentId> \
  --argument '{"sessionCookie":"...","profileUrls":["https://www.linkedin.com/in/..."]}'

# 2. Poll until data.is_running is false. Two views:
heliox tool phantombuster -- container get --id <containerId>            # status / endType / exitCode
heliox tool phantombuster -- agent output --id <agentId> --from-pos 0    # incremental console; echo data.output_pos next loop
heliox tool phantombuster -- container output --id <containerId> --from-pos <n>

# 3. Fetch the structured result (data.resultObject is a JSON string; parse it)
heliox tool phantombuster -- container result --id <containerId>

# List past runs of a Phantom, or abort a running one
heliox tool phantombuster -- container list --agent-id <agentId>
heliox tool phantombuster -- agent abort --id <agentId>
```

Poll politely (a few seconds between calls) and always advance `--from-pos` with
the returned `data.output_pos` so you fetch only new output.

## Result files

`container result` returns the structured rows inline (`data.resultObject`, a
JSON string). If a human wants a downloadable file, `agent get` exposes the
Phantom's `s3Folder`; combined with the org's `s3Folder` (from `org get`) the
public result URL is
`https://phantombuster.s3.amazonaws.com/<orgS3Folder>/<s3Folder>/result.csv`
(or `.json`). That S3 URL is public/unauthenticated. Hand it to the user, the
tool does not download it.

## Not supported here

Creating/editing/deleting Phantoms (script authoring), CRM contact saving, and
launching **workflows** are out of scope. Chain individual Phantoms instead.

## Errors

| Error | Meaning | What to do |
| --- | --- | --- |
| `ok:false` `code:api` `status:401/403` | API key rejected | Ask the user to reconnect with a fresh workspace key |
| `ok:false` `code:api` `status:429` | Over execution-time quota | Stop; run `org resources`, wait or ask the user to upgrade (the run's output is lost) |
| `ok:false` `code:usage` | Bad flags / invalid `--argument` JSON | Fix the command; nothing was sent |

## Safety

Launching a Phantom is an outward-facing action (it consumes quota and can send
outreach or scrape at scale). Follow the sensitive-operation rule from
`../SKILL.md` and confirm intent before launching a Phantom that contacts
people. Never echo the API key.
