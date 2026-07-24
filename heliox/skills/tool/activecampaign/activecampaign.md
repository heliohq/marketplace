# heliox tool activecampaign

ActiveCampaign marketing automation & CRM over the v3 REST API. A flat provider
(`heliox tool activecampaign -- ...`) with a larger command surface: contacts,
lists, tags, deals, pipelines/stages, campaigns, automations and custom fields.

## Connect (key entry, not OAuth)

ActiveCampaign has no OAuth. The user connects by pasting **two** values, both
found in ActiveCampaign under **Settings → Developer**:

- **Account URL** — the per-account API base, e.g. `https://youraccount.api-us1.com`
  (the `api-usN` data-center segment is shown there; it is not the app URL).
- **API key** — the `Api-Token` secret.

```bash
heliox tool activecampaign auth --json
```

Relay the link; the user pastes the account URL + API key through the connect
form. You are woken when the connection lands — do not poll. There is no consent
screen and no scopes. A wrong key is not caught at connect time; it surfaces as a
`401 reconnect required` on the first command (ask the user to reconnect).

## Use

Everything after `--` goes to the tool. Output is the provider's JSON verbatim.

```bash
# Contacts (the core object)
heliox tool activecampaign -- contact list --limit 20 --query email=jane@example.com
heliox tool activecampaign -- contact get 42
heliox tool activecampaign -- contact create --email jane@example.com --first-name Jane
heliox tool activecampaign -- contact update 42 --data '{"phone":"+15551234"}'
heliox tool activecampaign -- contact delete 42

# Segmentation
heliox tool activecampaign -- list list
heliox tool activecampaign -- contact subscribe --list 2 --contact 42 --status 1   # 1=subscribe, 2=unsubscribe
heliox tool activecampaign -- tag list
heliox tool activecampaign -- tag create --name vip --type contact
heliox tool activecampaign -- contact tag --contact 42 --tag 3
heliox tool activecampaign -- contact untag <contactTagId>

# CRM
heliox tool activecampaign -- deal list --query 'filters[stage]=5'
heliox tool activecampaign -- deal create --data '{"title":"Big deal","value":"10000","currency":"usd"}'
heliox tool activecampaign -- pipeline list        # deal groups
heliox tool activecampaign -- stage list           # deal stages

# Reporting & automations
heliox tool activecampaign -- campaign list
heliox tool activecampaign -- automation list
heliox tool activecampaign -- contact automate --contact 42 --automation 9
heliox tool activecampaign -- field list           # custom field ids
heliox tool activecampaign -- account list         # B2B accounts
```

## Notes

- **Pagination** is `--limit` (default 20, max 100) + `--offset`; the body's
  `meta.total` is the count. List commands do not auto-paginate — ask for the
  next page explicitly.
- **`--query key=value`** (repeatable) passes ActiveCampaign filters through
  verbatim, e.g. `--query 'filters[status]=1'`, `--query search=jane`.
- **`--data '<json>'`** on create/update supplies arbitrary v3 fields; the tool
  wraps it under the resource key (`{"contact":…}`, `{"deal":…}`) for you.
- Sending or changing contact data is outward-facing — follow the
  sensitive-operation rule in `../SKILL.md` before writes.
- Rate limit is 5 requests/second per account; a `429` surfaces as a plain
  command error — back off and retry, don't treat it as a connection problem.
