# Meta Ads (`heliox tool meta-ads -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Meta Ads is a
**flat provider**: everything after `--` is the Meta Ads tool's own CLI,
speaking the Meta Marketing API (Facebook Graph) with the connected account's
OAuth user token.

```bash
heliox tool meta-ads -- <resource> <verb> [flags...]
```

Resources: `accounts`, `campaign`, `adset`, `ad`, `creative`, `insights`. Run
`-- <resource> --help` (and `-- <resource> <verb> --help`) for the full flag
surface.

## The mental model (account → campaign → ad set → ad)

A Facebook user commonly has access to **many ad accounts** across several
businesses. The connection identity is the *user*, not one ad account, so
**you pass `--account act_<id>` on every account-scoped command**. It is never
connection state. Start by discovering which accounts you can operate on:

```bash
heliox tool meta-ads -- accounts list --json
```

Each row is an ad account (`id` in `act_<number>` form, `name`, `currency`,
`account_status`, `amount_spent`). Pick the `act_<id>` and pass it downward.
The object hierarchy is **Ad Account → Campaign → Ad Set → Ad**, with creatives
attached to ads and insights available at every level.

## Reading structure

```bash
heliox tool meta-ads -- campaign list --account act_123 [--status ACTIVE]
heliox tool meta-ads -- adset   list --account act_123 [--campaign <campaign_id>]
heliox tool meta-ads -- ad      list --account act_123 [--adset <adset_id>]
heliox tool meta-ads -- creative list --account act_123
heliox tool meta-ads -- campaign get <campaign_id>          # also: adset get, ad get
```

`list` commands page with `--limit` and `--after <cursor>` (the cursor comes
from `paging.cursors.after` in the previous page). Use `--fields a,b,c` to
select exactly the fields you need.

## Reading performance ("how did my ads do")

`insights` is the reporting command. Target **exactly one** of a whole account
(`--account`) or a single object (`--object <campaign|adset|ad id>`), aggregate
at `--level`, over a preset or explicit window:

```bash
heliox tool meta-ads -- insights --account act_123 --level campaign --date-preset last_7d
heliox tool meta-ads -- insights --object 456 --level ad \
  --time-range '{"since":"2026-01-01","until":"2026-01-31"}'
```

`--date-preset` (e.g. `today`, `last_7d`, `last_30d`, the default) and
`--time-range` are mutually exclusive. Default fields cover impressions,
clicks, spend, reach, CPM/CPC/CTR, frequency, and actions.

## Changing spend state (pause / resume / budget)

Status and budget live on the object; update by id. **Budgets are integers in
the ad account currency's minor unit (cents)**: `--daily-budget 5000` means
50.00 in a USD account.

```bash
heliox tool meta-ads -- campaign update <id> --status PAUSED
heliox tool meta-ads -- adset    update <id> --status ACTIVE --daily-budget 5000
heliox tool meta-ads -- ad       update <id> --status PAUSED
```

Creating a campaign requires an objective and (per Meta) a special-ad-category
declaration, which defaults to none:

```bash
heliox tool meta-ads -- campaign create --account act_123 \
  --name "Spring launch" --objective OUTCOME_TRAFFIC --status PAUSED
```

New campaigns default to `PAUSED` so nothing spends before you review it.

## Output and errors

`--json` emits a structured envelope; the default is human-readable. Exit codes
are **0** success, **1** runtime/API failure, **2** usage/parse. A Graph API
error is surfaced with its `type`/`code`/`message`; **code 190**
(`OAuthException`, expired/invalid token) is reported as a reconnect-needed
condition. Ask the user to re-authorize Meta Ads rather than retrying.
