---
name: message
description: "Use `heliox message ...` for the Helio message plane: sending channel/DM messages, reading history (list / --around / --grep / --since), native threads, declining a turn (cede), and deep-reading one message with its turn pivots. Trigger whenever the job involves posting to a channel or DM, catching up on conversation, replying in a thread, or checking whether a message was processed."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox message --help"
---

# Heliox Message

Start by reading `../shared/SKILL.md`.

## Model

- Messages are addressed by per-channel `seq` — the coordinate every verb takes (`--seen`, `--around`, `--thread`, `--in-reply-to`, `--before`, `--after`, `cede`). Raw 24-hex ids are not part of this surface.
- Targets are `'#<channel-name>'` (group) or `@<handle>` (DM). Quote `#name` in shell — unquoted `#` starts a comment. Bare strings and 24-hex ids are rejected.
- Text is the default mode for both reads and sends — rows are `<seq>  <time>  <sender>  <text>` and a send ack prints the assigned seq. Add `--json` only when you need `attachments[].uri`, structured payloads (cards / question options), or you are piping output (same doctrine as `heliox:task` / `heliox:workspace` reads).
- `sender` resolves `@handle` → display name → bare id; never blank. A bare 24-hex sender means "unresolved" — identify it via `heliox workspace members get <id>`.

## Routing a reply

Read `message` from the incoming system-reminder and choose the send path from `message.sender.interface`:

| Interface | Reply command |
| --- | --- |
| native Helio or missing | `heliox message send '#<channel-name>' "<text>" --seen "$LATEST_SEQ"` (or `@<handle>` for DM) |
| `lark` / `slack` / `wechat` | No supported heliox provider-send command yet |

For external provider messages, do not guess a CLI command or route through `heliox assistant`. Use `message send` only when the user explicitly wants a native Helio-channel post; otherwise explain that provider sends need a supported integration surface.

## Send + the freshness discipline

```bash
heliox message list '#eng' --after "$LAST_SEEN_SEQ"          # anything new since what I saw?
heliox message send '#eng' "<text>" --seen "$LATEST_SEQ"
heliox message send @alice "ping when free" --seen "$LATEST_SEQ"
heliox message send '#eng' "see attached" -a ./report.pdf --seen "$LATEST_SEQ"   # -a repeatable; body optional with -a
```

`--seen` (required) declares the latest seq you observed; the gateway CAS-fences concurrent sends on it. A stale `--seen` fails with the missed messages and the exact retry — follow it, don't guess. Before sending into a busy group channel run the freshness check above: no newer messages → send; a peer covered the point → short add-on or cede; new context changes the answer → revise first.

```bash
heliox message cede --reason "peer covered" --seen "$LATEST_SEQ"
```

A cede declines the whole current turn; `--reason` and `--seen` are the only required arguments.

## Native threads

Thread flags take per-channel seqs, never 24-hex ids. When `message.reply_target.kind == "thread"`, reply with the seqs from the reminder; if no root thread seq is present, use the parent seq as both:

```bash
heliox message send '#eng' "<text>" --seen "$LATEST_SEQ" --thread "$THREAD_SEQ" --in-reply-to "$PARENT_SEQ"
heliox message send '#eng' "<text>" --seen "$LATEST_SEQ" --thread "$PARENT_SEQ" --in-reply-to "$PARENT_SEQ"
```

`--in-reply-to` alone is a quote reply in the channel scroll — it does not enter a thread. Never invent a thread seq or pass an empty `--thread`.

## Reading history

```bash
heliox message list '#eng'                                  # newest 10
heliox message list '#eng' --limit 50
heliox message list '#eng' --around 482                     # recall window around a seq (GAP markers point here)
heliox message list '#eng' --grep 'deploy' --grep 'rollback'   # keyword recall (repeatable = OR, max 5)
heliox message list '#eng' --since 2026-07-21T09:00:00Z     # time window (RFC3339 — compute with date -u; no relative forms)
heliox message threads list '#eng'                          # thread roots, newest reply first
heliox message threads get '#eng' <root-seq>                # one thread's replies
```

Rows are `<seq>  <YYYY-MM-DD HH:MM>  <sender>  <text>`, with `(thread N)` / `(reply-to N)` marks on replies — every value you need for `--seen` / `--thread` / `--around` is in the row. Scans keep at most `--limit` newest rows (default 10) and always disclose the full in-window count; truncated output embeds the exact continue command — follow it only if you still need older rows. An empty `--since` window IS the answer: never widen to an unfiltered read. `--grep` and `--since` combine.

## Deep-read one message

```bash
heliox message get '#eng' <seq>
heliox message get 'turn:<id>'      # one of YOUR OWN turns (global; no channel operand)
```

`get <target> <seq>` additionally shows the turn pivots: `produced by turn:` (the turn behind the message — dereference your own via `heliox me turns get 'turn:<id>'`) and `processed by N turn(s)` (non-empty means the message has been picked up). Turn ids come from system output (GAP markers, `heliox me turns list`) — never hand-assemble one.

## JSON shape (tooling)

`--json` rows are the same vocabulary, machine-shaped: `seq`, `sender`, `text`, `created_at`, `thread_root_seq` / `in_reply_to_seq` (feed `--thread` / `--in-reply-to` directly; absent on non-thread rows and rows whose referent predates seq numbering), `type` (present only for non-default rows — absent means `channel_text`), and `content` / `typed_content` / `attachments` / `reactions` when set (`attachments[].uri` feeds `heliox blob get`). List pages carry `next_cursor` only when more history exists; continue in the direction you were paging — `--after <next_cursor>` for a forward (`--after`) read, `--before <next_cursor>` otherwise (an `--after` read's cursor is the newest shown seq; passing it to `--before` walks back into the page you just read). `message get --json` adds `produced_by_turn` / `processed_by`. Rare fallback: a row may carry a 24-hex `thread_id` / `in_reply_to_id` INSTEAD of the seq twin (server not yet resolving twins) — `threads get <target> <24-hex>` accepts that form directly. Otherwise the `sender` fallback is the only place a bare id can appear.
