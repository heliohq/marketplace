# Expensify (`heliox tool expensify`)

Expensify's Integration Server API: read policies and export report / expense
data, and submit any job Expensify supports. One connected account per
Expensify credential pair.

## Connect (once, by the user)

Expensify uses a **partnerUserID + partnerUserSecret pair**, not OAuth. The
user generates it at <https://www.expensify.com/tools/integrations/> (shown
once) and pastes it into the Helio connect drawer as a single value:

```
partnerUserID:partnerUserSecret
```

You cannot generate it for them. Send the connect link with
`heliox tool expensify auth --json`, explain what you need Expensify for, and
wait for the `oauth_connected` wake — do not poll.

## Model

Every Expensify call is one POST to a single endpoint carrying a
`requestJobDescription` JSON job `{type, credentials, inputSettings}`. Helio
injects the credentials; you supply the job. `--json` is always on; the
provider's JSON is emitted verbatim. A rejected credential surfaces as an
`APPROVAL_REQUIRED`/credential error — ask the user to reconnect.

## Commands

Read policies:

```bash
# List the policies (workspaces) the account can see
heliox tool expensify -- policy list [--admin-only] [--user-email <email>]

# Get details for specific policies
heliox tool expensify -- policy get --policy-id <ID> [--policy-id <ID> …] \
  [--field categories|reportFields|tags|tax|employees …] [--user-email <email>]
```

Anything else — report export/download, expense/report create, updates,
reconciliation — goes through the raw `request` escape hatch. Pass the full
`requestJobDescription` body **without** `credentials` (Helio adds them):

```bash
# Export combined report data to CSV (returns a generated file name),
# then download it in a second call.
heliox tool expensify -- request --input '{
  "type":"file",
  "inputSettings":{"type":"combinedReportData","filters":{"reportIDList":"R00bCluvcO4T,R006AseGxMka"}},
  "outputSettings":{"fileExtension":"csv"}
}'

heliox tool expensify -- request --input '{"type":"download","fileName":"<name-from-export>.csv"}'
```

Top-level `type` is one of `get | create | update | file | download |
reconciliation`. See the Integration Server docs
(<https://integrations.expensify.com/Integration-Server/doc/>) for each job's
`inputSettings`. Never put `credentials` in `--input`.

## Notes

- Rate limit: 5 requests / 10 s and 20 requests / 60 s (HTTP 429). Batch and
  pace calls.
- The report exporter needs a Freemarker `template`; that path is not wired
  into `request` yet — for templated exports, prefer a policy/report read plus
  your own formatting.
