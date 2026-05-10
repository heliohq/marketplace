# heliohq/marketplace

Public Claude Code plugin marketplace published by [Helio](https://helio.im).

## Install

```sh
claude plugin marketplace add github:heliohq/marketplace
claude plugin install heliox@heliohq
claude plugin install skill-creator@heliohq
```

## Plugins

- **heliox** — agent-facing CLI organized as domain skills
- **skill-creator** — create, modify, and improve other Claude Code skills

## Source of truth

Plugin source lives in the [helio](https://github.com/sheet0/helio) monorepo
under `agents/skills/`. **This repo is a publish target — do not edit
plugins here directly.** Submit changes upstream; the next sync run
republishes them.

The directory layout here mirrors `helio/agents/skills/`:

```
.claude-plugin/marketplace.json   ← upstream agents/skills/.claude-plugin/marketplace.json
heliox/                           ← upstream agents/skills/heliox/
skill-creator/                    ← upstream agents/skills/skill-creator/
```

## License

Each plugin carries its own LICENSE. The marketplace metadata itself is
released under MIT.
