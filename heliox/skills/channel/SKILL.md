---
name: channel
description: "Use Heliox channel commands for posting in any chat surface that includes humans or mixed AI+human membership: native Helio channels (DM and group), external Lark/Slack/WeChat replies, channel history, attachments, channel members, deleting channels, and opening solo coding sessions. Trigger whenever the assistant needs to reply to a human, post in a group channel, recover channel history, attach files, cede a turn, or spawn a `shipx-claude` solo coding environment. For private 1:1 messages strictly between two AI users (no humans involved), use `heliox:assistant` instead — that surface is the assistant DM API and never lands in a human-visible channel."
user-invocable: false
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox channel --help"
---

# Heliox Channel

Start by reading `../shared/SKILL.md`; it owns routing, JSON, thread, attachment, and freshness rules.

## Common native commands

| Intent | Command |
| --- | --- |
| Send message | `heliox channel send <channel_id> "<msg>" --json` |
| Send in native thread | `heliox channel send <channel_id> "<msg>" --thread <thread_root_id> --in-reply-to <message_id> --json` |
| Send files | `heliox channel send <channel_id> "attached" --file ./a.png --file ./b.pdf --json` |
| Cede turn | `heliox channel cede <channel_id> --reason "<why>" --json` |
| Recent history | `heliox channel messages <channel_id> --json` |
| Freshness check | `heliox channel messages <channel_id> --after <last_seen_msg_id> --json` |
| Older page | `heliox channel messages <channel_id> --before <cursor_msg_id> --json` |
| Download attachments | `heliox channel attachments download <channel_id> <message_id> --json` |

`channel send` requires either message text or at least one `--file`.

## External integration sends

Use these when `message_json.sender.interface` is external:

```bash
heliox integration lark send --channel "$CHANNEL_ID" --text "message"
heliox integration lark send --channel "$CHANNEL_ID" --reply-to "$EXTERNAL_MESSAGE_ID" --text "message"
heliox integration slack send --channel "$CHANNEL_ID" --text "message"
heliox integration wechat send --channel "$CHANNEL_ID" --text "message"
```

The `--channel` value is the Helio external channel id, not the provider's own chat id. Lark supports `--reply-to`; Slack and WeChat do not.

## Channels and members

```bash
heliox channel list --json
heliox channel list --type group --json
heliox channel list --type solo --json
heliox channel create --name "name" --json
heliox channel create --name "private name" --private --json
heliox channel members <channel_id> --json
heliox channel members add <channel_id> <user_id> --role member --json
heliox channel members add <channel_id> <user_id> --role admin --json
heliox channel members remove <channel_id> <user_id> --json
heliox channel delete <channel_id> --force --json
```

Delete channels sparingly. Only delete channels whose lifecycle you own, such as a solo runtime channel you created and no longer need.

## Update channel metadata

```bash
heliox channel update <channel_id> --name "<new name>" --json
heliox channel update <channel_id> --description "<text>" --json
heliox channel update <channel_id> --visibility public --json
heliox channel update <channel_id> --visibility private --json
heliox channel update <channel_id> --archive --json
heliox channel update <channel_id> --unarchive --json
```

`channel update` requires at least one of `--name`, `--description`, `--visibility`, `--archive`, or `--unarchive`. `--archive` and `--unarchive` are mutually exclusive. Prefer `--archive` over `delete` for channels the team may want back later.

## Solo coding environments

When work needs code changes, tests, or commands, open a solo coding channel instead of writing code inline:

```bash
heliox channel create --type solo --runtime-profile shipx-claude --initial-prompt "<brief>" --json
```

Rules:

- Only `shipx-claude` is supported as `--runtime-profile`.
- Write `--initial-prompt` as the full work order: what to do, why, constraints, tests, and what done means.
- The response is a `CreatedChannel` object with `id`, `name`, `type`, `visibility`, and `runtime_profile`.
- Use the returned `id` for follow-up channel commands.
- Before opening a new coding environment, check whether an existing solo channel already has the context:

```bash
heliox channel list --type solo --json
```

Follow up with:

```bash
heliox channel send <solo_channel_id> "<additional instruction>" --json
heliox channel messages <solo_channel_id> --json
```
