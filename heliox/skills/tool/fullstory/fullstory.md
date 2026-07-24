# FullStory (`heliox tool fullstory -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. FullStory is a
**flat provider** (not grouped like `google`): everything after `--` is the
fullstory tool's own CLI, calling the FullStory Server API v2.

```bash
heliox tool fullstory [--account <key>] -- <resource> <verb> [flags...]
```

Connect is a **pasted API key**, not an OAuth consent: the user creates a key
in FullStory (Settings → Integrations → API Keys, shown once) and enters it in
the connect link. The key is long-lived; there is no refresh.

## What it's for

The high-value flow is **investigating a user**: given an application user id
(`uid`) or email, pull up their recent session-replay URLs, then read or enrich
their profile. Plus server-side instrumentation: record a custom event or
upsert a user's properties.

## Commands

### Sessions — the investigation entry point

```bash
# Most recent session replay URLs for a user (results[].{id, fs_url, created_time})
heliox tool fullstory -- session list --uid <app-user-id> [--limit 10]
heliox tool fullstory -- session list --email <user@example.com>
```

Prefer **one** of `--uid` or `--email` (passing both queries each separately and
returns the union). Each result's `fs_url` opens the replay in FullStory; `id`
is the `deviceId:sessionId` session identifier.

### Users

```bash
# Find users by uid and/or email
heliox tool fullstory -- user list --uid <app-user-id>
heliox tool fullstory -- user list --email <user@example.com>

# Get one user by their FullStory-assigned id (from a list/session result)
heliox tool fullstory -- user get --id <FS_USER_ID> [--include-schema]

# Create or update a user by uid (upsert). Custom properties omit type suffixes.
heliox tool fullstory -- user upsert --uid <app-user-id> \
  --display-name "Ada Lovelace" --email ada@example.com \
  --prop pricing_plan=paid --prop total_spent=14.55 --prop vip=true
```

`--prop k=v` is repeatable; numeric and boolean values are sent typed
(`14.55` → number, `true` → boolean), everything else as a string. A user's
`uid` is immutable once set.

### Events

```bash
# Record a custom event against a user (by uid) or a specific session
heliox tool fullstory -- event create --name "Support Ticket" --uid <app-user-id> \
  --prop priority=Normal --prop source=Email
heliox tool fullstory -- event create --name "Support Ticket" --session-id <deviceId:sessionId>

# Stitch the event into the user's most recent session (needs --uid)
heliox tool fullstory -- event create --name "Checkout" --uid <app-user-id> --use-recent
```

Supply exactly **one** identity: `--uid` (a user) or `--session-id` (a session).
`--use-recent` is a modifier on the `--uid` path.

### Key check

```bash
# Verify the key and see its permission role (USER / ARCHITECT / ADMIN)
heliox tool fullstory -- me
```

## Permission & availability notes

- **Sending data** (`user upsert`, `event create`) and **`session list`** work
  with a **Standard** key.
- **Reading user data** (`user get`, `user list`) generally needs an
  **Architect** (Enterprise) key; on a Standard key these return a permission
  error — run `me` to check the key's role.
- Session-event capture, AI session summaries, and bulk import/export are part
  of separate FullStory products and are **not** wrapped here.

## Output & errors

Every command prints provider JSON to stdout; list-style calls keep FullStory's
`{"results":[...]}` envelope. Add `--json` for a structured error envelope.
Exit codes: `0` success, `1` API/runtime failure (the FullStory message is
surfaced — including a `429` monthly server-event quota reason), `2` a usage
error (bad flag combination) before any request is made.
