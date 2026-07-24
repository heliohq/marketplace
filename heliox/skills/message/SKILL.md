---
name: message
description: "Use `heliox message ...` for the Helio message plane: sending channel/DM messages, reading history (list / --around / --grep / --since), native threads, declining a turn (cede), and deep-reading one message with its turn pivots. Trigger whenever the job involves posting to a channel or DM, catching up on conversation, replying in a thread, or checking whether a message was processed."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox message --help"
---

# Heliox Message

## Model

- Messages are addressed by per-channel `seq` — the coordinate every verb takes (`--seen`, `--around`, `--thread`, `--in-reply-to`, `--before`, `--after`, `cede`). Raw 24-hex ids are not part of this surface.
- Targets are `'#<channel-name>'` (group) or `@<handle>` (DM). Quote `#name` in shell — unquoted `#` starts a comment. Bare strings and 24-hex ids are rejected.
- Two read shapes: text rows (`<seq>  <time>  <sender>  <text>`) for a quick scan, `--json` when you'll parse fields — `attachments[].uri`, structured payloads (cards / question options), or the seq twins. A send ack prints the assigned seq either way.
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

- `--seen` (required) declares the latest seq you observed; the gateway CAS-fences concurrent sends on it. A stale `--seen` fails with the missed messages and the exact retry — follow it, don't guess.
- Before sending into a busy group channel, run the freshness check above, then act on what came back:
  - no newer messages → send
  - a peer already covered the point → short add-on, or cede
  - new context changes your answer → revise first

Rich or multi-line body — backticks, `$`, apostrophes, newlines — gets shell-mangled. Don't hand-escape or flatten to plain text to dodge it; use `--args-file` instead:

- Write the whole invocation as a JSON array to a file: `["message","send","#eng","…full markdown body…","--seen","<seq>"]`.
- Run `heliox --args-file <path>` — nothing else on the line.
- The array holds the **literal body text**, never a draft-file path in a value (`--body` / `--procedure` / `--content`) — a future runtime can't read a file that only existed here.

## Cede — decline the turn

```bash
heliox message cede --reason "peer covered" --seen "$LATEST_SEQ"
```

Declines the whole current turn — the most common message verb. Only `--reason` and `--seen` are required.

## Native threads

Thread flags take per-channel seqs, never 24-hex ids. When `message.reply_target.kind == "thread"`, reply with the seqs from the reminder; if no root thread seq is present, use the parent seq as both:

```bash
heliox message send '#eng' "<text>" --seen "$LATEST_SEQ" --thread "$THREAD_SEQ" --in-reply-to "$PARENT_SEQ"
heliox message send '#eng' "<text>" --seen "$LATEST_SEQ" --thread "$PARENT_SEQ" --in-reply-to "$PARENT_SEQ"
```

`--in-reply-to` alone is a quote reply in the channel scroll — it does not enter a thread. Never invent a thread seq or pass an empty `--thread`.

## Reading history

```bash
heliox message list '#eng'                    # newest 10 (--limit N for more)
heliox message list '#eng' --around 482       # recall window around a seq (GAP markers point here)
heliox message threads list '#eng'            # thread roots, newest reply first
heliox message threads get '#eng' <root-seq>  # one thread's replies
```

Rows are `<seq>  <YYYY-MM-DD HH:MM>  <sender>  <text>`, with `(thread N)` / `(reply-to N)` marks on replies — every value you need for `--seen` / `--thread` / `--around` is in the row.

Recall filters (rare): `--grep <pat>` (repeatable = OR, max 5) for a keyword, `--since <RFC3339>` for a time window. Both scan recent history, keep the newest `--limit` rows, disclose the full in-window count, and embed the exact continue command when truncated. An empty `--since` window IS the answer — never widen to an unfiltered read.

## Deep-read one message

```bash
heliox message get '#eng' <seq>
heliox message get 'turn:<id>'      # one of YOUR OWN turns (global; no channel operand)
```

`get` also shows turn pivots: `produced by turn:` (the turn behind the message — dereference your own via `heliox me turns get`) and `processed by N turn(s)` (non-empty = picked up). Turn ids come from system output; never hand-assemble one.

## Attachments

- **Incoming**: may already be materialized under `.helio/attachments/…` (prefer the path in the runtime message context). Otherwise fetch by URI — a row's `attachments[].uri` (from `--json`) → `heliox blob get <uri> -o <file>` (binary-safe; omit `-o` for stdout). Not materialized? `heliox channel attachments download '#eng' <seq> --json`.
- **Sending**: `-a <file>` on `message send` (repeatable, order preserved; body optional with `-a`).
- Keep generated files in the workspace, not `/tmp`, when they may be reused.

## JSON shape (tooling)

`--json` rows carry the same vocabulary as the text rows, machine-shaped.

Fields:

- `seq`, `sender`, `text`, `created_at` — always present. `sender` is the only field a bare 24-hex id can surface in (its last-resort fallback).
- `thread_root_seq` / `in_reply_to_seq` — feed `--thread` / `--in-reply-to` directly; absent on non-thread rows.
- `type` — present only for non-default rows; absent means `channel_text`.
- `content` / `typed_content` / `attachments` / `reactions` — only when set (`attachments[].uri` feeds `heliox blob get`).
- `message get --json` also adds `produced_by_turn` / `processed_by`.

Paging — a page carries `next_cursor` only when more history exists; continue in the direction you were paging:

- `--after` read → continue `--after <next_cursor>` (the cursor is the newest shown seq; `--before` would walk back into the page you just read).
- any other read → continue `--before <next_cursor>`.
