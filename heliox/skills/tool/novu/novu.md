# Novu (`heliox tool novu -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Novu is a
**flat provider** (not grouped like `google`): everything after `--` is the
novu tool's own CLI. Novu is **notification infrastructure**: one `event
trigger` fans a workflow out to a subscriber or topic across whatever channels
(in-app, email, SMS, push, chat) that workflow defines.

```bash
heliox tool novu [--account <key>] -- <group> <verb> [flags...]
```

The credential is a Novu **environment secret key** (Dashboard → Developer →
API Keys, per environment). It is region-scoped: a key connected against the US
region works against `api.novu.co` only. Output is the provider JSON verbatim;
add `--json` for the structured error envelope on failures.

## Command groups

| Group | Verbs | Use |
|---|---|---|
| `event` | `trigger`, `bulk`, `broadcast`, `cancel` | Send: trigger a workflow to a recipient. The core action. |
| `subscriber` | `list`, `get`, `create`, `update`, `delete`, `preferences`, `set-preferences` | Manage recipients + their email/phone identifiers and opt-in state. |
| `topic` | `list`, `create`, `get`, `add-subscribers`, `remove-subscribers` | Audiences: group subscribers for broadcast-to-segment sends. |
| `workflow` | `list`, `get` | Read-only: discover the trigger identifier `event trigger` needs. |
| `message` | `list`, `delete` | Inspect delivered messages (filter by channel / subscriber / transaction). |
| `activity` | `list`, `get` | The activity feed; debug a triggered run. |
| `integration` | `list`, `active` | Read-only: which channel providers are configured. |

## The #1 footgun: HTTP 201 does NOT mean "delivered"

`event trigger` returning `201` (and `acknowledged: true`) means only that Novu
**accepted** the trigger, not that anything was sent. The load-bearing field
is `data.status`:

- `processed`: the success state.
- `trigger_not_active` · `no_workflow_active_steps_defined` ·
  `no_workflow_steps_defined` · `no_tenant_found` · `invalid_recipients` ·
  `error`: accepted but **not delivered**. Read `data.error[]` for the reason
  and `data.activityFeedLink` to inspect.

Always check `data.status == "processed"`, never just `transactionId`.

## Send a notification

```bash
# to one subscriber by id
heliox tool novu -- event trigger --workflow <trigger-id> --to <subscriberId> \
  --payload '{"name":"Ada"}' --json

# to a topic (or an array / rich subscriber object); pass raw JSON
heliox tool novu -- event trigger --workflow <trigger-id> \
  --to-json '{"type":"Topic","topicKey":"weekly-digest"}' --json

# discover the trigger id first if you don't know it
heliox tool novu -- workflow list --json
```

`--transaction-id <id>` deduplicates: re-triggering with the same id is ignored
by Novu. `--actor` / `--tenant` accept either a bare id string or a JSON object.

## Recipients and audiences

```bash
heliox tool novu -- subscriber create --subscriber-id user-42 --email a@b.co --first-name Ada
heliox tool novu -- subscriber list --email a@b.co --limit 20 --json
heliox tool novu -- topic create --key weekly-digest --name "Weekly digest"
heliox tool novu -- topic add-subscribers --key weekly-digest --subscriber-ids user-42,user-77
```

## Notes

- **API versions are mixed** (handled for you): events/messages/activity/
  integrations are Novu v1; subscribers/topics/workflows are Novu v2. You never
  type a version; the tool builds the right path per command.
- List verbs take `--limit` and cursor (`--after`/`--before`) or `--page`
  pagination depending on the resource; the response carries the paging fields.
- Exit codes: `0` success, `1` API/runtime failure (`--json` gives an
  `{"error":{kind,status,message}}` envelope; a `401` means the key was
  rejected; reconnect), `2` usage/parse error.
