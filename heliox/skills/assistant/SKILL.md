---
name: assistant
description: "Use `heliox assistant ...` for AI teammate lifecycle and AI-channel inspection: list teammates, show another AI's profile/channel metadata, create/delete an AI teammate, choose a model provider, or inspect the runtime hosts / local nodes an assistant can run on (`heliox assistant node list`). Trigger whenever the task involves spawning, retiring, or inspecting an AI teammate, picking a model provider (helio / host / a BYO key), or discovering runtime hosts / node ids. **For reading or sending AI DMs**, use `heliox message list @<handle>` / `heliox message send @<handle> ... --seen <seq>` — assistant message verbs are retired. External chat integration setup and provider sends currently have no supported heliox CLI surface."
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

```bash
heliox assistant create --name "<name>" --model claude-sonnet-4-6 --json
heliox assistant delete @helga --yes --json
```

`--model` is required unless `--provider host`. Use `claude-sonnet-4-6`
(balanced default), `claude-opus-4-7` (most capable), or
`claude-haiku-4-5-20251001` (fastest) — the user can ask for a specific one or
you pick sonnet.

`--provider` selects the model source; it defaults to `helio`:

- `helio` (default) — Helio-managed quota. Omit `--provider` for this.
- `host` — the target node's own claude/codex CLI login. Local node only, so
  pass `--node <local-node-id>` (see below). `--model` is optional here; the CLI
  fills the engine's host-family flagship when omitted.
- a **BYO provider name** — an org key/subscription. Pass the provider's name
  (not an id); list them with `heliox assistant provider list`.

```bash
heliox assistant provider list --json
heliox assistant create --name "<name>" --provider host --node <local-node-id> --json
heliox assistant create --name "<name>" --provider "<byo-name>" --model <model-id> --json
```

Adding a BYO provider (pasting an API key / connecting a subscription) is a
desktop flow — `heliox assistant provider create` returns guidance with a deep
link; relay it to the user. Runtime hosts and device pairing live under
`heliox assistant node` — see [node.md](node.md).

Create a new AI teammate only after the user asks for one or clearly accepts it. After creation, send a concrete first briefing with `heliox message send @<new-handle> "<briefing>" --seen "$LATEST_SEQ" --json`.

Delete only when explicitly requested.

## External chat integrations

`heliox assistant` does not manage Lark, Slack, or WeChat adapter setup. There is also no supported heliox CLI command for provider sends yet. Do not guess a command; ask for a supported integration surface or use native Helio channels only when the user explicitly wants to post into Helio.
