# Google Meet (`heliox tool google meet -- ...`)

Read [google.md](./google.md) for auth and account selection. Everything after
`--` is the meet tool's own CLI. Meet's value is **post-meeting**: who
attended, how long, and the transcript; Calendar handles scheduling, Meet does
not.

## Core commands

```bash
# Find meetings (conferenceRecords.list, newest first). Convenience flags and
# --filter both expand into the native EBNF filter; combine freely.
heliox tool google meet -- records list --after 2026-07-01T00:00:00Z --json
heliox tool google meet -- records list --space abc-mnop-xyz --json      # by meeting code
heliox tool google meet -- records list --ongoing --json                 # conferences still live
heliox tool google meet -- records get <record> --json                   # start/end/expire + space

# Who attended, and for how long
heliox tool google meet -- participants list <record> --json             # displayName + join/leave window
heliox tool google meet -- participants sessions <participant> --json     # per-reconnect segments

# Transcript: summarize from the stitched text, not raw entries
heliox tool google meet -- transcripts list <record> --json              # state + Docs documentId + exportUri
heliox tool google meet -- transcripts text <transcript>                 # full transcript as `speaker: text`
heliox tool google meet -- transcripts text <transcript> --save ./notes/meeting.txt

# Recordings / smart notes: index only (fileId + browser exportUri), no download
heliox tool google meet -- recordings list <record> --json
heliox tool google meet -- smart-notes list <record> --json              # served under /v2beta/ (GA methods)

# Ad-hoc meeting link (no calendar event) + reversible config
heliox tool google meet -- spaces get <space | meeting-code> --json
heliox tool google meet -- spaces create --access-type trusted --auto-transcription on --json
heliox tool google meet -- spaces update <space> --auto-recording on      # patch: only the flags you pass change
```

Check `-- --help` rather than guessing flags. Resource args accept the bare id
or the full resource name (`r1` or `conferenceRecords/r1`); `spaces get` also
accepts a meeting code directly.

## Summarizing a meeting: use `transcripts text`

To summarize "yesterday's call" or "what did X commit to", find the record
(`records list --after ...`), then `transcripts text <transcript>`: it pages
through every entry, resolves speaker names, orders by time, and hands you one
readable block. **Never** loop `transcripts entries` page by page to build a
summary; the synthetic verb exists precisely so you don't. The text comes from
the Meet API entries and can differ slightly from the edited Google Docs file.

## The 30-day window is a hard limit

`conferenceRecord` and its transcript entries are **server-deleted ~30 days
after the meeting ends** (`expireTime`). Past that, `records get` returns 404
and there is nothing to retry. Say so. The Drive recording/transcript **files**
may still exist, but this tool has no download capability (v1); offer the
`exportUri` from `recordings list` / `transcripts list` so the user can open
them in a browser.

## `spaces end-conference`: confirm first, always

```bash
heliox tool google meet -- spaces end-conference <space>
```

This **removes everyone currently in the call** in real time. Run it only when
the user gives an explicit instruction about *this specific meeting*, and
restate the effect ("this will end the meeting and disconnect all participants")
before you do. Never call it as a cleanup or housekeeping step on your own.

## Boundary: Meet is not Calendar

Scheduling, rescheduling, and inviting people are calendar operations: Meet
does not do them. `spaces create` only mints an instant link with no event, no
time, no invitees. To schedule a meeting or send invites, use
[heliox tool google calendar](./calendar.md) instead: create an event with a
Meet link attached (connect the calendar app first if it isn't yet).

## Failure notes

- **No connection / new account**: run `heliox tool google auth meet` and relay
  the link; multiple accounts → disambiguate with `--account` (see google.md).
- **403 with a scope hint**: the connection predates a needed `meetings.*`
  scope; ask the user to disconnect and reconnect (fresh consent re-grants all
  three scopes).
- **Empty recordings / transcripts / smart-notes list is not an error**: the
  meeting had them turned off, or the account's Google Workspace edition can't
  generate them (consumer/free accounts can't). Report the empty result and
  explain; do not retry or downgrade.
- **`records get` 404**: past the 30-day retention window (above).
- **smart-notes uses the /v2beta/ URL (GA methods)**: it may still be
  unavailable on some accounts (Workspace edition / feature not enabled); treat
  a not-enabled response as a capability gap, not a bug.
