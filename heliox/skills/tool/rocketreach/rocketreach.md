# RocketReach (`heliox tool rocketreach -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. RocketReach is
a **flat provider** (not grouped): everything after `--` is the rocketreach
tool's own CLI. It is a contact-enrichment / prospecting database — find people
and companies, and enrich a known person into verified emails and phone numbers.

```bash
heliox tool rocketreach [--account <key>] -- <resource> <verb> [flags...]
```

Auth is an API key (connect once via the portal). Every command prints the
provider JSON on stdout; add `--json` for a structured error envelope on
failure. Lookups spend a finite **credit balance** — check it before big runs.

## The mental model (read this first)

1. **Enrichment is asynchronous.** `person lookup` does NOT return emails/phones
   immediately. It returns a record with a `status` field
   (`complete` | `searching` | `waiting` | `progress` | `failed`). When the
   status is not yet `complete`, poll `person status --ids <id>` until it is.
   Emails and phones populate as the status reaches `complete`. Credits are
   charged only on a match.
2. **Search finds, lookup enriches.** `person search` returns matching profiles
   (name / title / employer / **profile id**) but **no contact info**. Take a
   profile id from the results and run `person lookup --id <id>` to enrich it.
3. **Check credits first.** `account` is free and non-consuming; read
   `credit_usage[].remaining` (`"inf"` when unlimited) before spending.

## Core commands

### Account / credits (free, non-consuming)

```bash
heliox tool rocketreach -- account
```

### Enrich a person (async)

```bash
# by name + employer, by LinkedIn URL, or by a profile id from a prior search
heliox tool rocketreach -- person lookup --name "Jane Doe" --current-employer "Acme"
heliox tool rocketreach -- person lookup --linkedin-url https://linkedin.com/in/janedoe
heliox tool rocketreach -- person lookup --id 807344

# poll the async lookup(s) until status is complete
heliox tool rocketreach -- person status --ids 807344,807345
```

### Find people to prospect

```bash
# common filters as flags; --json-query for the full RocketReach query object
heliox tool rocketreach -- person search --name "Jane Doe" --current-employer Acme --title VP --page-size 10
heliox tool rocketreach -- person search --json-query '{"current_title":["VP Sales"],"location":["New York"]}'
```

### Companies

```bash
heliox tool rocketreach -- company lookup --domain acme.com
heliox tool rocketreach -- company search --name Acme
heliox tool rocketreach -- company search --json-query '{"industry":["software"]}'
```

## Typical flow

```bash
# 1. budget check
heliox tool rocketreach -- account
# 2. find candidates (ids only, no contact info)
heliox tool rocketreach -- person search --current-employer Acme --title "VP Sales" --page-size 5
# 3. enrich a chosen profile id
heliox tool rocketreach -- person lookup --id 807344
# 4. if status != complete, poll
heliox tool rocketreach -- person status --ids 807344
```

## Footguns

- **Do not treat a `person lookup` response as final.** If `status` is not
  `complete`, the emails/phones are not populated yet — poll `person status`.
- **`person search` never returns contact info.** It returns profile ids to
  enrich; the emails/phones come only from `person lookup`.
- **Credits are finite.** A `429` means you hit a rate or credit limit, not a
  bad key. Run `account` to see the remaining balance.
- **`--json-query` takes a JSON object**, and its query fields are arrays
  (`{"current_title":["VP"]}`), matching RocketReach's search schema. Explicit
  flags (`--name`, `--title`, …) override the same key from `--json-query`.
