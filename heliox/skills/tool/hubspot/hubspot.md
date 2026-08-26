# HubSpot (`heliox tool hubspot -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. HubSpot is a
**flat provider** (not grouped like `google`): everything after `--` is the
HubSpot tool's own CLI.

```bash
heliox tool hubspot [--account <key>] -- <resource> <verb> [flags...]
```

HubSpot is the CRM system of record. The tool wraps the CRM v3/v4 object surface
(contacts, companies, deals, tickets), engagements (notes, tasks), associations
between records, plus owners, pipelines, and property schemas. Every command
prints the provider's own JSON on stdout.

## The mental model (read this first)

- **Portals are heavily customized.** Deal stages, pipelines, and custom
  properties differ per account. **Do not hardcode property or stage names**.
  Discover them with `property list` and `pipeline list` before writing.
- **Reads return only default properties** unless you ask for more: pass
  `--properties a,b,c` to project the fields you need.
- **Records are linked by associations**, not foreign keys. To see a contact's
  deals or attach a note to a company, use `assoc` / the engagement `--contact`
  `--company` `--deal` `--ticket` flags.

## Look someone up before acting

```bash
# who is this? (contact by email, then their open deals)
heliox tool hubspot -- contact get jane@acme.com --by-email --properties email,firstname,lastname,company --json
heliox tool hubspot -- contact search --filter "email:EQ:jane@acme.com" --properties email,hs_object_id --json

# search: --filter is property:operator[:value] (repeatable, AND); operators are
# HubSpot's (EQ, NEQ, GT, GTE, LT, CONTAINS_TOKEN, HAS_PROPERTY, IN, ...)
heliox tool hubspot -- deal search --filter "dealstage:EQ:appointmentscheduled" --sort createdate:desc --limit 20 --json
```

## Keep the CRM current

```bash
# create / update use --prop key=value (repeatable); values may contain '='
heliox tool hubspot -- contact create --prop email=jane@acme.com --prop firstname=Jane --json
heliox tool hubspot -- deal update 123 --prop dealstage=closedwon --prop amount=5000 --json
heliox tool hubspot -- company create --prop name="Acme Inc" --prop domain=acme.com --json

# delete archives the record
heliox tool hubspot -- ticket delete 456 --json
```

Object groups `contact | company | deal | ticket` all share the same verbs:
`get <id>` · `list` · `create` · `update <id>` · `delete <id>` · `search`.

## Log work and follow-ups

```bash
# a note, attached to records (hs_timestamp defaults to now)
heliox tool hubspot -- note create --body "Called the customer, sending proposal" --contact 581751 --deal 123 --json

# a task with a due date and owner
heliox tool hubspot -- task create --subject "Send proposal" --due 2026-08-01T09:00:00Z --owner 555 --contact 581751 --json
heliox tool hubspot -- task complete 789 --json
```

## Route and interpret

```bash
# owners (for assignment / --owner ids)
heliox tool hubspot -- owner list --email rep@acme.com --json

# pipelines + stages (to interpret and set dealstage / ticket stage)
heliox tool hubspot -- pipeline list deals --json

# property schema (discover a portal's custom fields before writing)
heliox tool hubspot -- property list deals --json
heliox tool hubspot -- property get deals dealstage --json

# associations (v4): link, list, unlink
heliox tool hubspot -- assoc create contact 1 company 2 --json
heliox tool hubspot -- assoc list deal 123 contact --json

# whoami / smoke: the connected portal
heliox tool hubspot -- account --json
```

## Footguns

- **`--filter` value order is `property:operator:value`.** `HAS_PROPERTY` /
  `NOT_HAS_PROPERTY` take no value (`amount:HAS_PROPERTY`). The value itself may
  contain `:`; only the first two `:` split the triple.
- **Search returns default properties only**. Add `--properties` to see the
  fields you filtered on.
- **Creating/updating an unknown property fails** with a validation error. Run
  `property list <objectType>` first if unsure of the exact internal name.
- **Sending outward-facing work** (a note or task the customer's rep will see):
  confirm content the way `../SKILL.md` describes before creating it.
