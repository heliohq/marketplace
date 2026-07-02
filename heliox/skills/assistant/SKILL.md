---
name: assistant
description: "Use `heliox assistant ...` for AI teammate lifecycle and AI-channel inspection: list teammates, show another AI's profile/channel metadata, or create/delete an AI teammate. Trigger whenever the task involves spawning, retiring, or inspecting an AI teammate. **For reading or sending AI DMs**, use `heliox message list @<handle>` / `heliox message send @<handle> ... --seen <seq>` — assistant message verbs are retired (design 160 §5). External chat integration setup and provider sends currently have no supported heliox CLI surface."
user-invocable: false
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox assistant --help"
---

# Heliox Assistant

Start by reading `../shared/SKILL.md`.

Use this for assistant lifecycle and AI-channel metadata inspection. Reading or sending messages to an AI uses `heliox message list @<handle>` / `heliox message send @<handle> ... --seen <seq>` (DM resolution is implicit when target is `@<handle>`); run `heliox message --help` for that surface.

## Addressing

Every verb here accepts the assistant handle in two equivalent shapes:

- bare handle — `helga`
- `@`-prefixed — `@helga`

24-hex ids are rejected; reverse-lookup via `heliox assistant list --json` if all you have is an id. `#`-prefixed inputs are rejected (those are channel names).

## List and inspect

```bash
heliox assistant list --json
heliox assistant show @helga --json
heliox message list @helga --limit 50 --json
```

`assistant show` includes the AI user's profile, DM channel metadata, and channel memberships. The old assistant-specific DM history verb was removed; read DM history through the normal message surface:

```bash
heliox message list @helga --limit 50 --json
heliox message send @helga "<text>" --seen "$LATEST_SEQ" --json
```

## Create and delete

`--model` is required. Use `claude-sonnet-4-6` (balanced default),
`claude-opus-4-7` (most capable), or `claude-haiku-4-5-20251001`
(fastest) — the user can ask for a specific one or you pick sonnet.

```bash
heliox assistant create --name "<name>" --model claude-sonnet-4-6 --json
heliox assistant delete @helga --yes --json
```

Create a new AI teammate only after the user asks for one or clearly accepts it. After creation, send a concrete first briefing with `heliox message send @<new-handle> "<briefing>" --seen "$LATEST_SEQ" --json`.

Delete only when explicitly requested.

## External chat integrations

`heliox assistant` does not manage Lark, Slack, or WeChat adapter setup. There is also no supported heliox CLI command for provider sends yet. Do not guess a command; ask for a supported integration surface or use native Helio channels only when the user explicitly wants to post into Helio.
