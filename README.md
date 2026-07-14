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
20 skills:

- **Communication** — `channel`, `channel-charter-creator`, `agent-collaboration` (deprecated alias), `email`, `meeting`
- **Work & knowledge** — `task`, `document`, `memory`, `workspace`, `user-guide`
- **Identity & access** — `profile`, `vault-approval`
- **Runtime & extensibility** — `apps`, `artifact`, `assistant`, `browser`, `plugin`, `skill`, `automation-creator`
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
under `agents/plugins/heliox/`. **This repo is a publish target — do not edit
plugins here directly.** Submit changes upstream; the next sync run
republishes them.

The Heliox payload here mirrors `helio/agents/plugins/heliox/`:

```
.claude-plugin/marketplace.json    Claude Code marketplace manifest
.agents/plugins/marketplace.json   Helio agent-runtime marketplace manifest
heliox/
  .claude-plugin/plugin.json       Claude Code plugin manifest
  .codex-plugin/plugin.json        Codex plugin manifest
  skills/                          20 domain skills
skill-creator/                     single-skill plugin (Claude Code)
```

## License

Everything here is Apache-2.0 — both plugins (declared in each `plugin.json`) and the
marketplace metadata. The full license text ships in `skill-creator/LICENSE.txt`.

## Publication protection

Heliox is published only by the post-deploy workflow in `sheet0/helio`. It
opens a same-repository `heliox-publish-vX.Y.Z` pull request; it never pushes
`main`. The required `heliox-marketplace-validate` check runs through the
default-branch `pull_request_target` workflow and executes validator code from
live `main` against the exact candidate revision as read-only data. It enforces synchronized
manifests/catalogs, loadable skill metadata, preservation of non-Heliox catalog
content, a strict version increase against freshly fetched `main`, exact
bot-branch naming, and payload-only changes. This merge-time comparison
prevents an older open publication PR from downgrading a newer version or
replacing the guard that judges it.

The `main` ruleset must require pull requests, this check, code-owner review,
stale-review dismissal, last-push approval, and strict up-to-date status checks,
with no publisher-App bypass. Bootstrap this guard PR under the current rules,
then make the check required and verify a test PR cannot merge while stale.
Keep the upstream `heliox-marketplace-publish` environment disabled until those
controls are active.
