---
name: shared
description: "Shared Heliox CLI rules for AI agents: operating posture, #/@ addressing conventions, `--json` discipline, bounded error recovery, attachment handling (`helio://` + blob get), and looking up command help instead of guessing flags. Trigger before issuing any `heliox ...` command in a turn so the baseline rules are loaded first — every other heliox skill assumes you have already read this one. Message-plane rules (send / list / threads / cede / freshness) live in `heliox:message`."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox --help"
---

# Heliox Shared

Use this skill as the baseline for every `heliox ...` action. Surface-specific rules live in their own skills: `heliox:message` (message plane), `heliox:task`, `heliox:workspace`, `heliox:channel`.

## Operating posture

- Text output is the default read mode across surfaces — a fraction of the JSON tokens. Add `--json` when you need field values to act on (uris, structured payloads) or when piping.
- If the command shape is uncertain, run `heliox <topic> --help` or `heliox <topic> <command> --help` first.
- Read stderr and structured JSON errors before retrying. Do not retry the same failing command unchanged.
- Unknown-flag recovery is bounded: at most one `--help` read, then one corrected retry that keeps the original scope — same target, same filters, same time window. Never recover from a failed *filtered* query by dropping the filters or switching to a wider list: that pulls unrelated data into your context and pollutes every judgment downstream. If a bounded query cannot express what you need, say so in your output instead of widening the read.
- Do not print secrets, tokens, passwords, or raw credential payloads.
- Treat delete, revoke, rotate, disconnect, uninstall, and restart as sensitive operations. Confirm user intent unless the current instruction already explicitly asked for that operation.

## Addressing

- Group channels are `'#<channel-name>'`, people are `@<handle>`. Bare strings and 24-hex ids are rejected at the CLI boundary.
- Quote `'#name'` in shell — bash treats an unquoted `#` at a word boundary as the start of a comment and silently truncates the rest of the line. `@handle` needs no quoting.
- When a surface shows you a bare 24-hex value (an unresolved sender, an id from a reminder), resolve it via `heliox workspace members get <id>` before using it in prose — ids never work as command targets.

## Attachments

Incoming attachments may already be materialized under `.helio/attachments/...`. Prefer the path shown in the runtime message context.

Sending: message sends and task create/comments all take `-a <file>` (repeatable; upload order preserved) — see `heliox:message` and `heliox:task` for the verb shapes.

Fetching by URI: Helio resource URIs use the `helio://` scheme; the one you see most is `helio://attachment/<att_id>` — emitted in task descriptions (image nodes), task/comment `attachments[]`, and message `attachments[]`. `heliox blob get` is the one-stop fetcher:

```bash
heliox blob get helio://attachment/att_892450...   # write to stdout (binary safe)
heliox blob get helio://attachment/att_892450... -o /tmp/shot.png
```

History download by channel + message seq (when the runtime didn't materialize locally):

```bash
heliox channel attachments download '#engineering' "$MESSAGE_SEQ" --json
```

Keep generated files in the workspace, not `/tmp`, when they may be attached or reused later.
