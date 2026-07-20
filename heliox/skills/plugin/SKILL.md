---
name: plugin
description: "Use `heliox plugin ...` to list, install, show, or uninstall Claude plugin bundles for this assistant. Trigger when the user asks what plugins/extensions are installed, asks to add/remove a marketplace plugin, or when a plugin install status/error needs inspection. For standalone SKILL.md files use `heliox:skill` instead."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox plugin --help"
---

# Heliox Plugin

Start by reading `../shared/SKILL.md`.

Plugins are assistant-scoped extension bundles: they can contain skills,
commands, hooks, agents, and MCP servers. `heliox plugin *` records desired
state in Helio; the runtime reconciler installs or removes the engine-side
plugin asynchronously.

For standalone `SKILL.md` uploads, use `heliox:skill`. Do not use
`heliox plugin install` for local paths, zip files, GitHub URLs, or raw
`SKILL.md` URLs.

## Ref shape

Install refs are marketplace refs:

```text
<plugin-name>@<marketplace>
```

Examples:

- `superpowers@superpowers-dev`
- `engineering@knowledge-work-plugins`

Other Claude ref shapes are not accepted here. The marketplace must already be
registered in Helio's marketplace registry.

## List and inspect

```bash
heliox plugin list --json
heliox plugin list --status installed --json
heliox plugin list --source preset --json
heliox plugin list --marketplace heliohq --json
heliox plugin show <plugin_id> --json
```

Use `list --json` to get the backend `id`; `show` and `uninstall` take that id,
not the `<name>@<marketplace>` ref.

## Install

```bash
heliox plugin install superpowers@superpowers-dev --json
heliox plugin install superpowers@superpowers-dev --no-wait --json
heliox plugin install superpowers@superpowers-dev --timeout 5m --json
```

Default install waits until the runtime reports `installed` or `failed`. Use
`--no-wait` when you are inside a turn and waiting would block useful work; then
inspect later with `heliox plugin show <plugin_id> --json`.

## Uninstall

```bash
heliox plugin uninstall <plugin_id> --yes --json
```

Uninstall only when the user explicitly asked for removal. Preset plugins are
locked; a `preset_locked` error means the assistant template must change rather
than removing that plugin from one assistant.

## Status semantics

| Status | Meaning | Agent action |
|---|---|---|
| `pending` | Backend accepted the row; runtime has not converged yet | Wait, or check later with `show` |
| `installed` | Runtime installed the plugin and reported a version when available | Tell the user it is ready |
| `failed` | Runtime could not install/uninstall the plugin | Read `error` via `show`; fix the cause before retrying |

Never retry the same failing plugin install unchanged.
