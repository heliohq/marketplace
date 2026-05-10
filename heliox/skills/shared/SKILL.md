---
name: shared
description: "Shared Heliox CLI rules for AI agents: routing replies from message_json, choosing native channel versus Lark/Slack/WeChat integration sends, using --json, handling errors, attachments, safety checks, and looking up command help instead of guessing flags. Trigger before issuing any `heliox ...` command in a turn so the routing, freshness, attachment, and safety rules are loaded first — every other heliox skill assumes you have already read this one."
user-invocable: false
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox --help"
---

# Heliox Shared

Use this skill as the baseline for every `heliox ...` action.

## Operating posture

- Prefer explicit arguments and `--json` whenever the command supports it.
- If the command shape is uncertain, run `heliox <topic> --help` or `heliox <topic> <command> --help` first.
- Read stderr and structured JSON errors before retrying.
- Do not retry the same failing command unchanged.
- Do not print secrets, tokens, passwords, or raw credential payloads.
- Treat delete, revoke, rotate, disconnect, uninstall, and restart as sensitive operations. Confirm user intent unless the current instruction already explicitly asked for that operation.

## Routing from message_json

Read `message_json` from the incoming system-reminder. Use `message_json.channel.id` as the Helio channel id for replies and command routing.

Choose the send path from `message_json.sender.interface`:

| Interface | Reply command |
| --- | --- |
| native Helio or missing | `heliox channel send <channel_id> "<text>" --json` |
| `lark` | `heliox integration lark send --channel <channel_id> --text "<text>"` |
| `slack` | `heliox integration slack send --channel <channel_id> --text "<text>"` |
| `wechat` | `heliox integration wechat send --channel <channel_id> --text "<text>"` |

For Lark only, when `message_json.external.message_id` exists, preserve provider context:

```bash
heliox integration lark send --channel "$CHANNEL_ID" --reply-to "$EXTERNAL_MESSAGE_ID" --text "message"
```

Slack and WeChat do not support `--reply-to` through heliox. Send a top-level provider message.

## Native threads

When `message_json.reply_target.kind == "thread"`, reply to
`message_json.reply_target.message_id`. If `message_json.reply_target.thread_id`
is present, include it as the root thread:

```bash
heliox channel send "$CHANNEL_ID" "message" --thread "$THREAD_ID" --in-reply-to "$PARENT_MESSAGE_ID" --json
```

Use `message_json.reply_target.thread_id` as `THREAD_ID` and
`message_json.reply_target.message_id` as `PARENT_MESSAGE_ID`. Do not use any
other ids unless the reminder says they are the reply target. Do not invent a
thread id or pass an empty `--thread`.

If the reminder does not include `reply_target.thread_id`, use the legacy-safe
form:

```bash
heliox channel send "$CHANNEL_ID" "message" --in-reply-to "$PARENT_MESSAGE_ID" --json
```

## Group-channel freshness check

Before sending into a busy group channel, fetch newer messages:

```bash
heliox channel messages "$CHANNEL_ID" --after "$LAST_SEEN_MESSAGE_ID" --json
```

- No newer messages: send.
- A peer covered the point: send a short add-on or cede.
- New context changes the answer: revise first.

Use `heliox channel cede "$CHANNEL_ID" --reason "peer covered" --json` when silence is intentional.

## Attachments

Incoming attachments may already be materialized under `.helio/attachments/...`. Prefer the path shown in the runtime message context.

To download historical message attachments:

```bash
heliox channel attachments download "$CHANNEL_ID" "$MESSAGE_ID" --json
```

To send files back to a native Helio channel:

```bash
heliox channel send "$CHANNEL_ID" "attached" --file ./report.pdf --json
heliox channel send "$CHANNEL_ID" "attached" --file ./one.png --file ./two.pdf --json
```

Keep generated files in the workspace, not `/tmp`, when they may be attached or reused later.

## Current command status

These commands are placeholders that error out with "not yet implemented". Do not route real work to them:

- `heliox act`
- `heliox config get`
- `heliox config set`
- `heliox onboard oauth`
- `heliox onboard register`
- `heliox onboard verify-email`
