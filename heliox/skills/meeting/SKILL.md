---
name: meeting
description: "Use `heliox meeting ...` for meeting participation. Trigger whenever the assistant needs to join a meeting, leave one, speak via TTS, send in-meeting chat, inspect participants, check session status, or read the meeting transcript. Also use this for meeting events whose source_type is transcript, meeting_chat, participant_join, participant_leave, or meeting_status."
user-invocable: false
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox meeting --help"
---

# Heliox Meeting

Start by reading `../shared/SKILL.md`.

Use this skill when the assistant needs presence inside a meeting.

## Join and leave

```bash
heliox meeting join "<meeting_url>" --channel-id <channel_id> --json
heliox meeting join "<meeting_url>" --channel-id <channel_id> --bot-name "<display name>" --json
heliox meeting leave --json
```

Optional overrides:

- `--org-id <org_id>` defaults from `HELIO_ORG_ID`.
- `--ai-user-id <ai_user_id>` defaults from `HELIOX_AI_USER_ID` or `HELIO_USER_ID`.

Join only when the context warrants attending. Do not join every link.

## Inside a meeting

```bash
heliox meeting status <session_id> --json
heliox meeting participants <session_id> --json
heliox meeting transcript <session_id> --json
heliox meeting transcript <session_id> --after <cursor> --json
heliox meeting chat <session_id> "<message>" --json
heliox meeting chat <session_id> "<message>" --to <participant_id> --json
heliox meeting speak <session_id> "<text>" --json
```

Use `transcript --after` for incremental reads instead of repeatedly fetching the whole transcript.

## Event handling

Meeting events arrive as channel messages with source metadata:

- `transcript`: accumulate context. Speak only when addressed or when you have real value.
- `meeting_chat`: reply inside the meeting with `heliox meeting chat`, not a Helio channel message.
- `participant_join` / `participant_leave`: update your awareness.
- `meeting_status`: on meeting ended, read transcript and post useful notes to the originating channel if there is a broader outcome.

If you process a transcript and decide not to speak, end with `heliox channel cede` (see `heliox:channel` for cede semantics):

```bash
heliox channel cede <message_json.channel.id> --reason "transcript - not addressed" --json
```

Reply in the medium you received: chat to chat, voice to voice. Post to the Helio channel only for things the broader team should see — `heliox channel send` for native channels, `heliox integration {lark,slack,wechat} send` for external integrations (see `heliox:channel`).
