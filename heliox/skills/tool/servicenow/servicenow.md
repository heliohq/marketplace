# ServiceNow (`heliox tool servicenow -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. ServiceNow is a
**flat provider** (not grouped like `google`): everything after `--` is the
servicenow tool's own CLI.

```bash
heliox tool servicenow [--account <key>] -- <group> <verb> [flags...]
```

ServiceNow is an enterprise ITSM / workflow platform. The tool wraps the
**Table API**: the single generic REST surface that reads and writes records in
any table (`incident`, `problem`, `change_request`, `task`, `sys_user`,
`kb_knowledge`, CMDB `cmdb_ci*`, `sc_request`, …). A thin `incident` convenience
group and a raw `api` escape hatch cover ergonomics and everything else.

## Connect (two-field credential: instance URL + API key)

ServiceNow credentials are **instance-scoped**: the instance host is part of
every request URL, so a connection needs **two** inputs, not one:

1. **Instance URL**: e.g. `https://acme.service-now.com` (your company's
   ServiceNow instance).
2. **REST API Key**: sent as the `x-sn-apikey` header.

There is **no ServiceNow-hosted OAuth** an outside app can use across arbitrary
customer instances, so this is a key-entry connection, not an OAuth consent.
The key is created **inside the customer's own instance** by an admin:

1. Activate the **API Key and HMAC Authentication** plugin
   (`com.glide.tokenbased_auth`, GA since the Washington release).
2. System Web Services → **API Access Policies** → create an **Inbound
   Authentication Profile** whose Auth Parameter is the `x-sn-apikey` **Auth
   Header** record.
3. Create a **REST API Key** linked to a dedicated integration **user**: that
   user's roles scope what the key can read/write (`Auth Scope = useraccount`).
4. Attach the profile to a **REST API Access Policy** targeting `/now/table/`.

**Admin footgun to relay when you ask the user to connect:** creating an API
Access Policy on a resource **locks that resource to the configured auth
method(s)**. Other methods (e.g. Basic) must be re-added as profiles, or
existing integrations on that resource can break. Scope the policy to the
integration's needs.

A bad key or wrong instance URL is not caught at connect time (no verify probe);
it surfaces on the first command as an auth error. Reconnect with corrected
values.

## Core commands

### Generic Table API (works on any table)

```bash
# list/query: sysparm encoded query; ^ = AND, ^OR = OR, field=value / field!=value / fieldLIKEx
heliox tool servicenow -- table query incident --query "active=true^priority=1" --limit 20 --fields number,short_description,state --json
heliox tool servicenow -- table get   incident <sys_id> --fields number,state --json
heliox tool servicenow -- table create change_request --data '{"short_description":"Patch db","type":"normal"}' --json
heliox tool servicenow -- table update incident <sys_id> --data '{"work_notes":"investigating"}' --json
heliox tool servicenow -- table delete incident <sys_id> --json
```

- `--display-value all|true|false` resolves reference/choice fields to their
  human labels (e.g. assignment_group name) instead of raw sys_ids
  (`sysparm_display_value`).
- `--limit` / `--offset` page results (`sysparm_limit` / `sysparm_offset`).
- Query results are returned as a **bare JSON array**; get/create/update as a
  **bare JSON object** (the Table API `{result}` envelope is unwrapped for you).

### Incident convenience group (accepts an INC number or a sys_id)

```bash
heliox tool servicenow -- incident list --query "assignment_group=Network^active=true" --limit 20 --json
heliox tool servicenow -- incident get    INC0010001 --json          # number OR sys_id
heliox tool servicenow -- incident create --short-description "VPN down for Sales" --data '{"urgency":"1"}' --json
heliox tool servicenow -- incident update INC0010001 --data '{"assigned_to":"<user sys_id>"}' --json
heliox tool servicenow -- incident resolve INC0010001 --close-notes "Rebooted the concentrator" --code "Solved (Permanently)" --json
```

`incident get/update/resolve` accept the **human INC number** (INC0010001) and
resolve it to `sys_id` for you via a lookup: you and humans speak incident
numbers, not sys_ids. A 32-hex sys_id is used directly. `resolve` sets
`state=6` (Resolved) with the close notes/code.

### Identity + raw escape hatch

```bash
heliox tool servicenow -- whoami --json                              # verify key + echo the integration user
# any /api/now/... endpoint (Aggregate, Import Set, Attachment, …); x-sn-apikey is injected
heliox tool servicenow -- api GET /api/now/stats/incident --query sysparm_count=true --json
heliox tool servicenow -- api POST /now/table/incident --body '{"short_description":"x"}' --json   # /now/... shorthand also works
```

Run `-- <group> --help` (or `-- <group> <verb> --help`) for exact flags rather
than guessing.

## Footguns (where agents go wrong)

- **Two-field connect.** Unlike most tools, ServiceNow needs BOTH an instance
  URL and an API key. When you ask the user to connect, name both.
- **Encoded-query syntax, not SQL.** `sysparm_query` uses `^` for AND, `^OR`
  for OR, and operators like `=`, `!=`, `LIKE`, `IN`, `>=`. Example:
  `active=true^priority=1^assignment_groupLIKENetwork`. There are no spaces
  around operators.
- **sys_id vs number.** Most tables key on the opaque `sys_id`. Incidents (and
  other task records) also carry a human `number` (INC…/CHG…/PRB…). The
  `incident` group accepts either; the generic `table get/update/delete` needs a
  **sys_id**: query by number first (`table query incident --query
  "number=INC0010001" --fields sys_id`) if you only have the number.
- **Reference fields are sys_ids.** `assigned_to`, `assignment_group`,
  `caller_id` etc. store sys_ids. Write them as sys_ids in `--data`; read them
  human-readable with `--display-value all`.
- **The `api` verb cannot override auth.** `--header x-sn-apikey:...` is
  rejected; the credential is injected and fixed.
- **`--account` when more than one ServiceNow instance is connected.** Dev/test/
  prod are separate connections; select with `--account <key>` (the instance
  base URL) before the `--`.

## Safety

- ServiceNow records (incidents, changes, work notes) are operational records
  others act on. Follow the sensitive-operation rule in
  [../SKILL.md](../SKILL.md) before creating, resolving, or reassigning
  anything. Confirm scope before a `table delete` or an `incident resolve`.
- Prefer `work_notes` (internal) vs `comments` (customer-visible) deliberately;
  a comment may notify the caller.
