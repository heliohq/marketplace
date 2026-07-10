---
name: shared
description: "Shared Heliox CLI rules for AI agents: routing replies from message, choosing native channel versus Lark/Slack/WeChat integration sends, using --json, handling errors, attachments, safety checks, and looking up command help instead of guessing flags. Trigger before issuing any `heliox ...` command in a turn so the routing, freshness, attachment, and safety rules are loaded first — every other heliox skill assumes you have already read this one."
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

## Routing from message

Read `message` from the incoming system-reminder. Address the destination by the resolved name, not the raw id: `'#<channel-name>'` for group channels, `@<handle>` for DMs. Bare strings and 24-hex ids are rejected at the CLI boundary.

Choose the send path from `message.sender.interface`:

| Interface | Reply command |
| --- | --- |
| native Helio or missing | `heliox message send '#<channel-name>' "<text>" --seen "$LATEST_SEQ" --json` (or `@<handle>` for DM) |
| `lark` | No supported heliox provider-send command yet |
| `slack` | No supported heliox provider-send command yet |
| `wechat` | No supported heliox provider-send command yet |

For external provider messages, do not guess a CLI command or route through `heliox assistant`. Use `heliox message send` only when the user explicitly wants a native Helio-channel post; otherwise explain that provider sends need a supported integration surface.

## Native threads

Native message thread flags take per-channel seqs, not Mongo ids. When
`message.reply_target.kind == "thread"`, reply to the parent seq from the
runtime reminder. If a root thread seq is present, include it as the root
thread:

```bash
heliox message send '#<channel-name>' "message" --seen "$LATEST_SEQ" --thread "$THREAD_SEQ" --in-reply-to "$PARENT_SEQ" --json
```

Use the `id:` seqs shown in the system reminder or message-list output. Do not
use raw 24-hex message ids for `--thread`, `--in-reply-to`, or `--seen`. Do not
invent a thread seq or pass an empty `--thread`.

If the reminder does not include `reply_target.thread_id`, use
the parent seq as both the thread root and direct reply target:

```bash
heliox message send '#<channel-name>' "message" --seen "$LATEST_SEQ" --thread "$PARENT_SEQ" --in-reply-to "$PARENT_SEQ" --json
```

`--in-reply-to` alone is a quote reply in the current channel scroll. It
does not enter a native thread.

## Group-channel freshness check

Before sending into a busy group channel, fetch newer messages:

```bash
heliox message list '#<channel-name>' --after "$LAST_SEEN_SEQ" --json
```

- No newer messages: send.
- A peer covered the point: send a short add-on or cede.
- New context changes the answer: revise first.

Use `heliox message cede --reason "peer covered" --seen "$LATEST_SEQ" --json` when silence is intentional. A cede declines the whole current turn — you do not enumerate message seqs; `--seen` (latest seq you observed) and `--reason` are the only required arguments.

## Fetch a single message by seq

When you already have a specific per-channel seq from a prior
`heliox message list --json`, from a reply target in the incoming reminder, or
from a quote chain, pull the message directly without re-listing:

```bash
heliox message get <channel-id> <message-seq> --json
```

Takes the raw channel-id plus per-channel seq pair (not the sigil-prefixed name
and not a 24-hex message id). Useful for re-reading the parent of a thread
reply, inspecting an attachment ref you saw mentioned earlier, or following a
quote chain back through the scroll.

## Attachments

Incoming attachments may already be materialized under `.helio/attachments/...`. Prefer the path shown in the runtime message context.

### Sending files

Native Helio channels and DMs accept attachments via the `-a` flag on `heliox message send` (repeat for multiple files; upload order is preserved):

```bash
heliox message send '#engineering' "see attached" -a ./report.pdf --seen "$LATEST_SEQ" --json
heliox message send @ada "two diffs" -a ./one.png -a ./two.pdf --seen "$LATEST_SEQ" --json
heliox message send '#engineering' -a ./screenshot.png --seen "$LATEST_SEQ" --json   # attachment-only; body optional
```

Tasks and task comments accept the same flag — see `heliox:task`:

```bash
heliox task create "<title>" --channel '#engineering' -a ./screenshot.png --json
heliox task comments add <task-id> "<body>" -a ./diff.patch --json
heliox task comments add <task-id> -a ./repro.log --json          # attachment-only comment
```

Image refs land inline in the task description (`![name](helio://attachment/...)`); non-image refs ride the `attachments[]` sidecar. Both kinds show up in the JSON `attachments[].uri` field — see "Fetching attachments by URI" below.

### Fetching attachments by URI

Helio resource URIs use the `helio://` scheme. The one you see most is `helio://attachment/<att_id>` — emitted in task descriptions (image nodes), task `attachments[]`, and comment `attachments[]`. Use `heliox blob get` to pull the bytes:

```bash
heliox blob get helio://attachment/att_892450...   # write to stdout (binary safe)
heliox blob get helio://attachment/att_892450... -o /tmp/shot.png
heliox blob get helio://attachment/att_892450... -o -   # explicit stdout
```

`heliox blob get` is the one-stop fetcher; use it for any `helio://attachment/...` you see in `task show --json`, `message list --json`, or a `task comments list --json` response.

### History download

To pull historical message attachments by channel + message id (used when the runtime didn't materialize them locally):

```bash
heliox channel attachments download "$CHANNEL_ID" "$MESSAGE_ID" --json
```

Keep generated files in the workspace, not `/tmp`, when they may be attached or reused later.
