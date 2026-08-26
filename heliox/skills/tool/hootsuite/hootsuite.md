# Hootsuite (`heliox tool hootsuite -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. Hootsuite is a
**flat provider**: everything after `--` is the Hootsuite tool's own CLI,
speaking the Hootsuite REST API v1 with the connected account's OAuth user
token. Hootsuite fans one post out to many connected social profiles (X,
LinkedIn, Facebook, Instagram, Pinterest, TikTok, …), on a schedule, with an
approval workflow.

```bash
heliox tool hootsuite [--account <key>] -- <resource> <verb> [flags...]
```

Resources: `me`, `org`, `profile`, `message`, `media`. Run `-- <resource>
--help` (or `-- message schedule --help`) for the full flag surface.

## The mental model (profiles first, then messages)

A **message** is one post scheduled to one or more **social profiles**. You
never post to a network directly. You post to a `socialProfileId`, which is a
specific connected account (a particular X handle, a particular LinkedIn page).
So the first job is always discovering the profile ids you may post to:

```bash
heliox tool hootsuite -- me                 # who am I + which organizations
heliox tool hootsuite -- profile list       # the social profiles + their numeric ids
```

Use the `id` values from `profile list` as `--profile` on a schedule.

## Scheduling a post

```bash
heliox tool hootsuite -- message schedule \
  --text "Launch day!" \
  --profile 118264228 --profile 220001111 \
  --send-time 2029-03-01T14:00:00Z
```

- `--profile` is repeatable; each value is a **numeric** social profile id from
  `profile list`. The post fans out to all of them.
- `--send-time` **must** be UTC ISO-8601 ending in `Z` (e.g.
  `2029-03-01T14:00:00Z`). Offset timestamps like `+02:00` are rejected before
  the request. Convert to UTC yourself. **Omit `--send-time` entirely** to send
  as soon as possible.
- Optional: `--tag <s>` (repeatable), `--email-notification` (email the author
  on send), `--media-id <id>` (repeatable; attach uploaded media, see below).

## Reviewing and unscheduling

```bash
heliox tool hootsuite -- message list --state SCHEDULED \
  --start 2029-01-01T00:00:00Z --end 2029-02-01T00:00:00Z --profile 118264228
heliox tool hootsuite -- message get <message-id>
heliox tool hootsuite -- message delete <message-id>       # unschedule / cancel
```

Approval workflow (when your org gates posts through reviewers):

```bash
heliox tool hootsuite -- message approve <message-id>
heliox tool hootsuite -- message reject <message-id> --reason "off-brand"
```

## Attaching media

Media is a two-step handshake: request an upload URL, PUT the bytes to it
yourself, poll until `READY`, then reference the id on a schedule:

```bash
heliox tool hootsuite -- media create --size-bytes 10240 --mime-type image/png
#   → { id, uploadUrl, expiresAt }. PUT your bytes to uploadUrl (outside heliox)
heliox tool hootsuite -- media get <media-id>   # poll until state READY
heliox tool hootsuite -- message schedule --text "..." --profile <id> --media-id <media-id>
```

Images and video cannot be mixed in one message, and video must be scheduled at
least 15 minutes in the future.

## Pinterest (special case)

A Pinterest post **cannot be bundled** with other profiles and needs a board +
destination. Pass exactly one `--profile` (the Pinterest one) plus:

```bash
heliox tool hootsuite -- message schedule --text "Pin it" \
  --profile 999 --board-id 12345678909876 --destination-url https://example.com
```

`--board-id` and `--destination-url` must be given together. Retrieve the board
id from Pinterest directly. Hootsuite does not return it.

## Footguns

- **Numeric profile ids.** `--profile` must be the numeric `id` from
  `profile list`, not a network name or handle. A non-numeric value is a usage
  error (exit 2), never sent.
- **UTC only.** Non-`Z` send/filter times are rejected locally. Always convert
  to UTC and append `Z`.
- **Soonest-possible vs scheduled.** No `--send-time` = send now; a `--send-time`
  = scheduled. Don't pass a past timestamp expecting "immediately".
- Output is the provider JSON with Hootsuite's `{"data": …}` envelope already
  unwrapped. Read the inner object/array directly.
