---
name: assistant
description: "Use `heliox assistant ...` for AI teammate lifecycle: show an AI's profile/channels, create or delete an AI teammate (optionally from an agent template via `template list --query`), pick a model provider, or inspect runtime nodes. Trigger whenever the task involves spawning, retiring, or inspecting an AI teammate, hiring from a template, choosing a model source (helio / host / BYO), or finding node ids. **To list AI teammates** use `heliox workspace members list --json` (`assistant list` is retired); **for AI DMs** use `heliox message list/send @<handle>` (assistant message verbs are retired)."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox assistant --help"
---

# Heliox Assistant

Surface split (three questions, three surfaces):

- *Who are the AI teammates?* → `heliox workspace members list --json` (rows carry `type: human|ai`, `handle`, `bio`). `assistant list` is retired.
- *Talk to an AI* → `heliox message list @<handle>` / `heliox message send @<handle> "<text>" --seen <seq>`.
- *Assistant-domain detail + lifecycle* → this skill.

Handles ride bare (`helga`) or `@`-prefixed (`@helga`). Raw 24-hex ids are rejected; reverse-lookup via `heliox workspace members get <id> --json`. `#`-prefixed inputs are channel names, rejected here.

## Inspect

```bash
heliox assistant show @helga --json
```

Returns the projected profile: `handle`, `name`, `bio`, `model`, `lifecycle_status`, `email`, `dm` (an `https://app.helio.im/dm/...` link), and `model_source` (`{provider, harness, provider_label}`, which model source and engine the assistant actually runs on; use it to diagnose host/BYO binding), plus channel memberships as `{name, kind}` rows. No raw platform ids.

## Create

```bash
heliox assistant create --name "<name>" --model claude-sonnet-4-6 --json
```

`--model` is required unless `--provider host`. Default to `claude-sonnet-4-6` (balanced); `claude-opus-4-7` (most capable) or `claude-haiku-4-5-20251001` (fastest) when the user asks for it. Create only after the user asks for a new teammate or clearly accepts one; after creation, send the new AI a concrete first briefing: `heliox message send @<new-handle> "<briefing>" --seen "$LATEST_SEQ" --json`. The create echo is the projected profile; poll `assistant show` until `lifecycle_status` is active if you need it awake.

### From a template

A template gives the new assistant a role identity (brain, skills, tool integrations) instead of the bare default. Refs are discovered, never guessed; an unknown ref fails the create:

```bash
heliox assistant template list --query "release" --json
heliox assistant create --name "<name>" --model <model> --template @helio/<slug> [--var KEY=VALUE ...] --json
```

The catalog is 300+ templates, so `template list` is a bounded page (default 30); always narrow with `--query` (matches ref, name, description, tags, specialties); `matched` in the envelope reveals truncation. Rows carry the `ref` that `--template` accepts, a `recommended_model` to use as `--model` when the user has no preference, and `required_vars`: every listed name needs a `--var NAME=value` on create (the create fails 4xx per missing one); no `required_vars` means no `--var` flags at all.

### Model provider and node

`--provider` picks the model source (default `helio`; managed quota, omit the flag):

```bash
heliox assistant provider list --json                      # every selectable --provider value + model menus
heliox assistant create --name "<n>" --provider host --node <local-node-id> --json
heliox assistant create --name "<n>" --provider "<byo-name>" --model <model-id> --json
```

- `host`: the node's own claude/codex CLI login. Local node only: pass `--node` with a node whose `host_cli` shows the engine as `found` (the probe statuses are `found` / `not_found` / `unknown`; `heliox assistant node list --json`, see [node.md](node.md)). `--model` may be omitted; the CLI fills the engine's flagship.
- BYO: an org key/subscription; select by **name** from `provider list` (never an id).

Adding a BYO provider or pairing a device are desktop flows: `provider create` / `node create` return a deep link to relay to the user.

## Delete

```bash
heliox assistant delete @helga --yes --json
```

Only when explicitly requested.

## Not on this surface

Lark / Slack / WeChat adapter setup and external-provider sends have no heliox CLI surface. Don't guess commands; ask for a supported integration surface, or use native Helio channels only when the user explicitly wants a Helio post.
