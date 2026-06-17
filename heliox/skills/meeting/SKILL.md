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
heliox meeting join "<meeting_url>" --channel <channel_id> --json
heliox meeting join "<meeting_url>" --channel <channel_id> --bot-name "<display name>" --json
heliox meeting join "<meeting_url>" --channel <channel_id> --language en --json
heliox meeting leave --json
```

`--channel` is the channel that originated the request to attend. When the meeting ends, server posts the "generate notes" trigger back to this channel — so it must reflect the conversation thread where the caller asked you to join, not your DM. There is no override flag for `ai_user_id` / `org_id`; the server reads them from the bearer claims on the runtime api-key.

Join only when the context warrants attending. Do not join every link.

## Inside a meeting

```bash
heliox meeting status <session_id> --json
heliox meeting participants <session_id> --json
heliox meeting transcript <session_id> --json
heliox meeting transcript <session_id> --last-minutes 5 --json
heliox meeting chat <session_id> "<message>" --json
heliox meeting chat <session_id> "<message>" --to <participant_id> --json
heliox meeting speak <session_id> "<text>" --json
```

`transcript --last-minutes N` returns only the trailing N minutes (plain-array mode). Without a filter the full transcript comes back.

## Event handling

Meeting events arrive as channel messages with source metadata:

- `transcript`: accumulate context. Speak only when addressed or when you have real value.
- `meeting_chat`: reply inside the meeting with `heliox meeting chat`, not a Helio channel message.
- `participant_join` / `participant_leave`: update your awareness.
- `meeting_status`: on meeting ended, read transcript and post useful notes to the originating channel if there is a broader outcome.

If you process a transcript and decide not to speak, end with `heliox message cede` (see `heliox:shared` for cede semantics):

```bash
heliox message cede <seq-1> [<seq-2> ...] --reason "transcript - not addressed" --seen <latest-seq-you-observed> --json
```

Reply in the medium you received: chat to chat, voice to voice. Post to the Helio channel only for things the broader team should see with `heliox message send`. External provider sends for Lark, Slack, or WeChat currently have no supported heliox CLI surface; do not guess a command.
