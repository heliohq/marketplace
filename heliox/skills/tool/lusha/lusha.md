# Lusha (`heliox tool lusha -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Lusha is a
**flat provider** (not grouped like `google`): everything after `--` is the
lusha tool's own CLI. Auth is a Lusha API key the user connected once; the CLI
injects it; you never handle the key.

```bash
heliox tool lusha [--account <key>] -- <resource> <verb> [flags...]
```

Lusha is B2B **contact and company** data: turn a partial lead (email /
LinkedIn URL / name+company) into verified emails, phones, titles, and
firmographics; or generate net-new leads matching an ICP and reveal only the
good ones. Every verb takes `--json` and returns a stable `{data, meta}`
envelope.

## The mental model (read this first)

There are **two discovery paths** feeding **one reveal step** per entity, plus a
usage check:

- **`enrich`**: you already hold a real-world identifier (email, LinkedIn URL,
  or name + company). One call → the revealed record. Use for "I have this
  person/company, fill in the rest."
- **`search`**: you have an ICP (job titles, seniority, location, company
  size/industry…), not specific people. Returns **name-only previews with Lusha
  `id`s** (no emails/phones) plus a `request_id`. Use to *generate* leads you
  didn't have.
- **`reveal`**: takes the Lusha `id`s a `search` returned and unlocks the full
  records. This is the credit-efficient path: **search cheaply, reveal only the
  rows that matter.**

`search` results are useless without `reveal`. Always carry the `id`s from a
search into the matching `reveal`.

## Contacts

```bash
# Enrich a known contact (POST /contacts/search-and-enrich). Give ONE identifier:
heliox tool lusha -- contact enrich --email jane@acme.com --json
heliox tool lusha -- contact enrich --linkedin-url https://linkedin.com/in/jane --json
heliox tool lusha -- contact enrich --first-name Jane --last-name Doe --company-domain acme.com --json
#   --reveal emails,phones   (omit = reveal both)

# Prospect net-new contacts by ICP filter (POST /contacts/prospecting).
# --filters is the raw Lusha filter object as JSON (see "Filters" below).
heliox tool lusha -- contact search \
  --filters '{"contacts":{"include":{"jobTitles":["VP Sales"],"seniorityIds":[5]}},"companies":{"include":{"countries":["US"]}}}' \
  --page 0 --size 25 --json
#   returns preview objects carrying `id` + a `request_id` in meta

# Reveal the contacts you picked from a search (POST /contacts/enrich).
heliox tool lusha -- contact reveal --id 4389064654 --id 4389064624 --reveal emails --json
#   up to 100 --id per call
```

## Companies

```bash
# Enrich a known company (POST /companies/search-and-enrich). NO --reveal flag:
# firmographics come back by default.
heliox tool lusha -- company enrich --domain acme.com --json
heliox tool lusha -- company enrich --name "Acme Inc" --json

# Prospect net-new companies by ICP filter (POST /companies/prospecting).
heliox tool lusha -- company search \
  --filters '{"companies":{"include":{"sizes":[{"min":50,"max":500}],"industries":["Software"]}}}' \
  --page 0 --size 25 --json

# Reveal companies from a search (POST /companies/enrich). The optional --reveal
# is a FIRMOGRAPHIC-EXPANSION enum, NOT emails/phones:
heliox tool lusha -- company reveal --id 16303253 \
  --reveal employeesByDepartment,competitors,intent --json
#   allowed: employeesByDepartment | employeesByLocation | employeesBySeniority | competitors | intent
```

## Account usage (check before you spend)

```bash
heliox tool lusha -- account usage --json
#   -> {data:{credits:{used,remaining,total}, plan, rateLimits, pricing}}
```

`account usage` is **credit-free**. Call it before a credit-heavy sweep to see
remaining credits and per-action pricing.

## Filters (`search` verbs)

`--filters` is the raw Lusha V3 prospecting filter object, passed through as
JSON. The top-level shape is `{contacts:{include,exclude}, companies:{include,exclude}}`
(company `search` uses only the `companies` branch). Common include fields:

- contacts: `jobTitles`, `seniorityIds`, `departments`, `countries`,
  `locations`, `names`.
- companies: `sizes` (`[{min,max}]`), `revenues`, `industries`, `technologies`,
  `countries`, `names`, `domains`.

`--page` is 0-based (0-1000); `--size` is 10-100 (default 25). `meta.has_more`
tells you whether to page again.

## Credits & billing (spend deliberately)

Charging differs by entity. It is not one flat "enrich = per-datapoint" rule:

- **`contact reveal`** (`/contacts/enrich`): charged **per revealed datapoint**
  (each email or phone), no search charge. If a search preview showed
  `canReveal.credits: 0`, that datapoint is already revealed for the account and
  re-revealing it is **free**.
- **`contact enrich`** (`search-and-enrich`). **Two** charges: one search +
  one per revealed datapoint.
- **`company reveal`** (`/companies/enrich`): charged **per successful company
  result** (companies expose no per-datapoint PII), via the `reveal_company`
  action.
- **`company enrich`** (`search-and-enrich`): charged **per successful result**
  (same `reveal_company` meter).
- **`contact search` / `company search`**: charged per result (search only).

So the credit-efficient contact flow is: **`contact search` (cheap sweep) →
filter to the rows you actually want → `contact reveal` on just those `id`s.**
Never reveal the rows you discard. `meta.credits_charged` on every response
reports what the call cost.

## Output envelopes

- `enrich` / `reveal` → `{data: [records], meta: {credits_charged,
  results_returned, request_id}}`. `data` is always an array.
- `search` → `{data: [previews], meta: {page, size, total, has_more,
  credits_charged, request_id}}`. Previews carry the Lusha `id`. Feed them into
  `reveal`.
- `account usage` → `{data: {credits, plan, rateLimits, pricing}}`.
- Errors → stderr `{error:{message, kind, status}}`, exit 1. A `401` means the
  key was rejected. Ask the user to reconnect Lusha.

## Footguns

- **`company enrich` has no `--reveal`.** The endpoint's schema has no reveal
  field; passing one is a mistake. Contact verbs use `emails,phones`; company
  `reveal` uses the firmographic-expansion enum only.
- **Rate limit:** `account/usage` is capped at ~5 req/min; the data endpoints
  have their own limits (see `meta`/`rateLimits`). A `429` is a plain retry, not
  a credential problem.
- **API keys are Premium/Scale-plan only**: a user on a lower tier cannot issue
  one.
