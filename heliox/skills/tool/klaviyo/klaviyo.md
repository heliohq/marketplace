# Klaviyo (`heliox tool klaviyo -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Klaviyo is a
**flat provider** (not grouped like `google`): everything after `--` is the
klaviyo tool's own CLI.

```bash
heliox tool klaviyo [--account <key>] -- <resource> <verb> [flags...]
```

Klaviyo is the e-commerce marketing hub. This tool wraps the JSON:API surface
(`https://a.klaviyo.com/api`) for the three jobs an assistant actually does:
**audience** (profiles / lists / segments), **messaging** (campaigns / flows /
templates), and **analytics** (metrics / events / reporting). Responses are
Klaviyo's JSON:API bodies passed through verbatim (a top-level `data` plus
`links.next` for pagination).

## The mental model (read this first)

- **Everything is JSON:API.** Reads return `{"data":[...],"links":{"next":...}}`;
  writes take a `{"data":{"type":...,"attributes":{...}}}` envelope. The tool
  builds that envelope for you on the common single-entity operations, and
  every write also accepts `--data '<raw json:api body>'` to override it for
  full control.
- **Cursor pagination.** A list returns at most one page. To get the next page,
  take `links.next`'s `page[cursor]` value and pass it as `--cursor`. `--page-size`
  (1–100) sets the page size.
- **Filters are Klaviyo's own grammar**, passed through verbatim via `--filter`,
  e.g. `equals(email,"amy@example.com")`, `greater-than(created,2024-01-01)`.

## Core commands

### Account (identity)

```bash
heliox tool klaviyo -- account get          # GET /accounts — the connected Klaviyo account
```

### Audience — profiles

```bash
heliox tool klaviyo -- profile list --filter 'equals(email,"amy@example.com")'
heliox tool klaviyo -- profile get <id>
heliox tool klaviyo -- profile create --email amy@example.com --external-id cust_42
heliox tool klaviyo -- profile update <id> --phone +15551234567

# consent — single-profile convenience over Klaviyo's bulk-job API (returns a 202 job receipt)
heliox tool klaviyo -- profile subscribe   --email amy@example.com --list-id <listId>          # email marketing
heliox tool klaviyo -- profile subscribe   --phone +15551234567 --channel sms --list-id <listId>
heliox tool klaviyo -- profile unsubscribe --email amy@example.com --list-id <listId>
heliox tool klaviyo -- profile suppress    --email amy@example.com     # stop all email marketing
heliox tool klaviyo -- profile unsuppress  --email amy@example.com
```

### Audience — lists & segments

```bash
heliox tool klaviyo -- list list
heliox tool klaviyo -- list get <id>
heliox tool klaviyo -- list create --name "VIP customers"
heliox tool klaviyo -- list profiles <id>                              # members of a list
heliox tool klaviyo -- list add-profiles <id> --profile-id P1 --profile-id P2
heliox tool klaviyo -- list remove-profiles <id> --profile-id P1

heliox tool klaviyo -- segment list
heliox tool klaviyo -- segment get <id>
heliox tool klaviyo -- segment profiles <id>                          # members of a segment
```

### Messaging — campaigns, flows, templates

```bash
# campaign list REQUIRES a channel (default email); --channel email|sms|mobile_push
heliox tool klaviyo -- campaign list --channel email
heliox tool klaviyo -- campaign get <id>
heliox tool klaviyo -- campaign messages <id>                         # the campaign's messages
heliox tool klaviyo -- campaign send --id <campaignId>                # trigger a send (202 job)

heliox tool klaviyo -- flow list
heliox tool klaviyo -- flow get <id>
heliox tool klaviyo -- flow status <id> --status live                 # draft | manual | live

heliox tool klaviyo -- template list
heliox tool klaviyo -- template get <id>
```

### Analytics — metrics, events, reports

```bash
heliox tool klaviyo -- metric list
heliox tool klaviyo -- metric get <id>
# aggregate is an open-ended query — supply the JSON:API body verbatim
heliox tool klaviyo -- metric aggregate --data '{"data":{"type":"metric-aggregate","attributes":{...}}}'

heliox tool klaviyo -- event list --filter 'equals(profile_id,"<id>")'
heliox tool klaviyo -- event get <id>
heliox tool klaviyo -- event create --metric "Placed Order" --email amy@example.com --value 29.99 --properties '{"order_id":"O-1"}'

# performance reports — values (aggregated) by default, --series for time-series
heliox tool klaviyo -- report campaign --data '{"data":{"type":"campaign-values-report","attributes":{"statistics":["opens","clicks"],"timeframe":{"key":"last_30_days"}}}}'
heliox tool klaviyo -- report flow --series --data '{"data":{"type":"flow-series-report","attributes":{...}}}'
```

Run `-- <resource> <verb> --help` for the exact flags rather than guessing.

## Shared query flags (every list command)

`--filter`, `--sort` (e.g. `-created`), `--cursor`, `--page-size` (1–100),
`--include` (comma-separated relationships), `--fields` (sparse fieldset for the
primary resource), and `--param name=value` (repeatable) for any other raw
query parameter (e.g. `--param 'additional-fields[profile]=subscriptions'`).

## Footguns (where agents go wrong)

- **`campaign list` requires a channel.** Klaviyo mandates a
  `messages.channel` filter on `GET /campaigns`; the tool surfaces it as
  `--channel` (default `email`). Passing `--filter` too is fine — the tool
  AND-combines your filter with the channel predicate.
- **Consent operations are async jobs.** `subscribe` / `unsubscribe` /
  `suppress` / `unsuppress` return a **202 job receipt**, not the updated
  profile. The change lands shortly after; re-read the profile to confirm state
  rather than treating the 202 as the final result.
- **SMS subscribe needs a phone.** `--channel sms` requires `--phone` (E.164);
  email subscribe needs `--email`.
- **Writes take a JSON:API envelope.** The convenience flags build it for the
  common cases; for anything richer (nested relationships, custom attributes),
  pass `--data '<full json:api body>'` — it wins over the shorthand.
- **`metric aggregate` and `report campaign|flow` are `--data`-only.** Their
  bodies (statistics, timeframe, conversion metric, filters) are open-ended, so
  there is no shorthand — supply the JSON:API body verbatim.
- **This is a read+operate surface, not a builder.** Campaign *creation* (the
  multi-step create → message → template → assign flow), catalogs, coupons, and
  webhooks are intentionally out of scope. You can read campaigns and trigger a
  prepared one's send, not author a new one.
- **A `401` means the connection needs re-auth**; a `429` is a rate limit —
  the tool reports it rather than retrying, so back off and retry yourself.
- **`--account` when more than one Klaviyo account is connected.** A `409` lists
  the candidate account keys; re-run with `--account <key>` (before the `--`).

## Safety

- Sending a campaign, subscribing, suppressing, or toggling a flow to `live` is
  an **outward-facing, hard-to-undo** action that reaches real customers —
  follow the sensitive-operation rule in [../SKILL.md](../SKILL.md) and confirm
  scope with the user before running one.
