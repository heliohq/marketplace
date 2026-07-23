# Salesforce (`heliox tool salesforce -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Salesforce is a
**flat provider** (not grouped like `google`): everything after `--` is the
salesforce tool's own CLI.

```bash
heliox tool salesforce [--account <key>] -- <command> [flags...]
```

The tool speaks the **Salesforce Platform REST API** against the connected
org's `instance_url` (its My Domain host — captured for you at connect time).
Every command prints the provider's JSON to stdout. Work in this order:
**describe → query → write**, so you build valid SOQL and record payloads from
the org's real object/field names instead of guessing.

## The mental model (read this first)

- Salesforce stores everything as **sObjects** (`Account`, `Contact`, `Lead`,
  `Opportunity`, `Case`, `Task`, plus custom objects ending in `__c`).
- You read data two ways: **SOQL** (`query`, precise, when you know the object
  and fields) and **search** (fuzzy, cross-object, when you have a name/term).
- Custom fields and picklist values differ per org. **Never assume field
  names** — run `sobject describe <Object>` first.
- Errors come back as a JSON **array**: `[{"errorCode":"...","message":"..."}]`.

## Discover the schema first

```bash
# list objects (trimmed: name/label/custom/queryable); filter to custom or standard
heliox tool salesforce -- sobject list --custom-only --json
# fields for one object (trimmed to name/label/type/required/updateable/picklist)
heliox tool salesforce -- sobject describe Opportunity --json
heliox tool salesforce -- sobject describe Account --field-names-only --json
# who am I / which org, and remaining API budget
heliox tool salesforce -- whoami --json
heliox tool salesforce -- limits --json
```

Add `--raw` to `sobject list`/`describe` for the full untrimmed body (large).

## Read

```bash
# SOQL — the primary read path (auto-follows pagination up to --max-records)
heliox tool salesforce -- query "SELECT Id, Name, StageName, Amount FROM Opportunity WHERE IsClosed = false ORDER BY CloseDate" --json
heliox tool salesforce -- query "SELECT Id FROM Lead WHERE Email = 'a@b.com'" --all --json   # queryAll = includes deleted/archived

# fuzzy cross-object search (SOSL) — use when you have a name, not an id
heliox tool salesforce -- search "Acme" --objects Account,Contact --fields Id,Name --limit 20 --json

# one record by id (optionally trim fields)
heliox tool salesforce -- record get Account 001XXXXXXXXXXXXXXX --fields Id,Name,Industry --json
```

SOQL values are single-quoted; escape a literal quote as `\'`. `query` merges
all pages into one `{totalSize, done, records:[...]}` envelope.

## Write

```bash
# create → returns {"id":"...","success":true}
heliox tool salesforce -- record create Lead --data '{"LastName":"Doe","Company":"Acme","Email":"a@b.com"}' --json

# update (PATCH) → 204, tool emits {"success":true,"id":"..."}
heliox tool salesforce -- record update Opportunity 006XX... --data '{"StageName":"Closed Won"}' --json

# delete → {"success":true,"id":"..."}
heliox tool salesforce -- record delete Task 00TXX... --json

# upsert by an external-id field (idempotent create-or-update)
heliox tool salesforce -- record upsert Account External_Id__c A-1001 --data '{"Name":"Acme Inc"}' --json

# log a call/task after a meeting
heliox tool salesforce -- record create Task --data '{"Subject":"Call: renewal","Status":"Completed","WhoId":"003XX...","WhatId":"006XX..."}' --json
```

`--data` accepts literal JSON, `@file`, or `@-` (stdin). Invalid JSON is a usage
error (exit 2), caught before any request.

## Footguns

- **Field names are org-specific.** A create/update that 400s with
  `INVALID_FIELD` or `REQUIRED_FIELD_MISSING` means describe the object and fix
  the payload — do not retry the same body.
- **`INVALID_SESSION_ID`** = the connection needs re-auth; surface it, don't
  loop.
- **`REQUEST_LIMIT_EXCEEDED`** = the org's daily API budget is spent; check
  `limits` and back off.
- **Ids are 15- or 18-char, case-sensitive.** Prefer the 18-char id SOQL
  returns.
- **`update`/`delete` return no body on success** (HTTP 204) — the tool
  synthesizes `{"success":true,...}` so a caller reading stdout still gets a
  result.

## Version

Commands hit `v65.0` of the REST API by default; override per call with
`--api-version v67.0` when you need a newer resource.
