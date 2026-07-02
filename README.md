# heliohq/marketplace

Public Claude Code plugin marketplace published by [Helio](https://helio.im).

## Requirements

The [Claude Code](https://docs.claude.com/en/docs/claude-code) CLI. heliox is also
published for Codex and the Helio agent runtime — see [Runtimes](#runtimes).

## Install

```sh
claude plugin marketplace add github:heliohq/marketplace
claude plugin install heliox@heliohq
claude plugin install skill-creator@heliohq
```

## Plugins

### heliox

The Helio agent-facing CLI, organized as domain skills. Each skill wraps a slice of
the `heliox` command surface so an AI teammate can operate Helio directly. It ships
17 skills:

- **Communication** — `channel`, `email`, `meeting`, `agent-collaboration`
- **Work & knowledge** — `task`, `document`, `memory`, `workspace`
- **Identity & access** — `profile`, `vault-approval`
- **Runtime & extensibility** — `assistant`, `browser`, `node`, `plugin`, `skill`, `automation-creator`
- **Shared** — `shared` (common CLI conventions the other skills build on)

### skill-creator

Create, modify, and improve Claude Code skills. Ships eval-runner scripts,
grader/analyzer/comparator agents, and an eval-viewer for benchmarking skill
performance.

## Runtimes

heliox is published to three runtimes; skill-creator targets Claude Code only.

| Manifest | Runtime | Plugins published |
|----------|---------|-------------------|
| `.claude-plugin/marketplace.json` | Claude Code | heliox, skill-creator |
| `.agents/plugins/marketplace.json` | Helio agent runtime | heliox |
| `heliox/.codex-plugin/plugin.json` | Codex | heliox |

## Source of truth

Plugin source lives in the [helio](https://github.com/sheet0/helio) monorepo
under `agents/skills/`. **This repo is a publish target — do not edit
plugins here directly.** Submit changes upstream; the next sync run
republishes them.

The directory layout here mirrors `helio/agents/skills/`:

```
.claude-plugin/marketplace.json    Claude Code marketplace manifest
.agents/plugins/marketplace.json   Helio agent-runtime marketplace manifest
heliox/
  .claude-plugin/plugin.json       Claude Code plugin manifest
  .codex-plugin/plugin.json        Codex plugin manifest
  skills/                          17 domain skills
skill-creator/                     single-skill plugin (Claude Code)
```

## License

Everything here is Apache-2.0 — both plugins (declared in each `plugin.json`) and the
marketplace metadata. The full license text ships in `skill-creator/LICENSE.txt`.
