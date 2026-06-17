# heliohq/marketplace

Public Claude Code plugin marketplace published by [Helio](https://helio.im).

## Install

```sh
claude plugin marketplace add github:heliohq/marketplace
claude plugin install heliox@heliohq
claude plugin install skill-creator@heliohq

codex plugin marketplace add heliohq/marketplace
codex plugin add heliox@heliohq
```

## Plugins

- **heliox** — agent-facing CLI organized as domain skills
- **skill-creator** — create, modify, and improve other Claude Code skills

## Source of truth

Plugin source lives in the [helio](https://github.com/sheet0/helio) monorepo
under `agents/plugins/`. **This repo is a publish target — do not edit
plugins here directly.** Submit changes upstream; the next sync run
republishes them.

The directory layout here mirrors `helio/agents/plugins/`:

```
.claude-plugin/marketplace.json   ← Claude marketplace manifest
.agents/plugins/marketplace.json  ← Codex marketplace manifest
heliox/                           ← upstream agents/plugins/heliox/
skill-creator/                    ← bundled skill-creator skill
```

## License

Each plugin carries its own LICENSE. The marketplace metadata itself is
released under MIT.
