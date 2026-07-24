# OneSignal (`heliox tool onesignal -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. OneSignal is a
**flat provider** (not grouped like `google`): everything after `--` is the
onesignal tool's own CLI.

```bash
heliox tool onesignal [--account <key>] -- <resource> <verb> [flags...]
```

OneSignal is a push / email / SMS customer-messaging platform. The connection
holds two values you never pass by hand: an **App API Key** (the secret) and an
**App ID** (which app to act on). The App ID is injected into every request
automatically — you target segments, users and messages, never apps.

## The mental model (read this first)

- One connection = one OneSignal **app**. The account key is the App ID.
- A **message** goes to exactly **one targeting method**: a segment, specific
  subscription ids, emails, phone numbers, or a filter expression — never more
  than one. The tool rejects two targeting methods before it calls OneSignal.
- A **segment** is a saved audience (filters). List segments first to get a
  valid `--segment` name before sending to one.

## Core commands

### Send a message

```bash
# push to a saved segment (the most common send)
heliox tool onesignal -- message send --channel push \
  --segment "Subscribed Users" --heading "Sale" --content "50% off today" --json

# email to specific addresses (heading = subject, content = body/HTML)
heliox tool onesignal -- message send --channel email \
  --email user@example.com --heading "Welcome" --content "<p>Hi there</p>" --json

# SMS to E.164 numbers
heliox tool onesignal -- message send --channel sms --phone +15551234567 --content "Your code is 123456" --json

# target by a JSON filter array instead of a segment
heliox tool onesignal -- message send --channel push \
  --filters '[{"field":"tag","key":"vip","relation":"=","value":"true"}]' \
  --content "VIP early access" --json

# schedule for later
heliox tool onesignal -- message send --channel push --segment "Subscribed Users" \
  --content "Reminder" --send-after "2026-08-01 09:00:00 GMT-0700" --json
```

Exactly one of `--segment`, `--subscription-id`, `--email`, `--phone`,
`--filters` per send (all repeatable except `--filters`). `--content` is
required; `--heading` is the push title / email subject.

### Inspect and cancel messages

```bash
heliox tool onesignal -- message list --limit 10 --json     # recent messages
heliox tool onesignal -- message get --id <notification-id> --json   # delivery stats
heliox tool onesignal -- message cancel --id <notification-id> --json # cancel a scheduled send
```

### Segments

```bash
heliox tool onesignal -- segment list --json                 # pick a valid --segment name from here
heliox tool onesignal -- segment create --name "VIPs" \
  --filters '[{"field":"session_count","relation":">","value":"10"}]' --json
heliox tool onesignal -- segment delete --id <segment-id> --json
```

### Users (by alias)

```bash
heliox tool onesignal -- user upsert --alias-label external_id --alias-id user-123 \
  --tags '{"plan":"pro"}' --properties '{"language":"en"}' --json
heliox tool onesignal -- user get --alias-label external_id --alias-id user-123 --json
```

## Output and errors

Every command prints the provider JSON on stdout. A successful send returns the
message `id` and recipient count. Exit codes: `0` success, `1` an API/runtime
error (`--json` prints `{"error":{"message","kind":"api","status"}}`), `2` a
usage error such as missing `--content` or two targeting methods (no request is
sent). A revoked App API Key surfaces as an API error on the next call.

## Footguns

- **One targeting method only.** `--segment X --email a@b.com` is rejected
  (exit 2). Pick one.
- **App ID is fixed by the connection.** There is no `--app-id`; to act on a
  different OneSignal app, connect that app as its own account.
- **App vs Organization keys.** This tool uses an **App API Key**. Creating
  apps or rotating keys needs an Organization API Key and is out of scope.
