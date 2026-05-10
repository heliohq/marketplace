---
name: status
description: "Use `heliox status` to introspect the AI runtime's own state: pod runtime id, brain-fragment hashes/sizes, and evolution changelog / reflection counts. Trigger whenever the assistant needs to answer 'is the brain in the state I expect?', verify a previous restart landed cleanly, check brain fragment hashes prior to a self-edit, or decide whether a restart is needed (preflight). For the AI's outward-facing profile (display name, email, avatar, rename), use `heliox:profile`. For workspace metadata or members, use `heliox:workspace`. For executing the restart itself and the self-edit lifecycle, use `heliox:evolve`."
user-invocable: false
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox status --help"
---

# Heliox Status

Start by reading `../shared/SKILL.md`.

This skill is about the AI runtime's own state: which pod runtime is active, what brain fragments are loaded, and whether a restart is warranted. For the AI's outward-facing profile (display name / email / avatar / rename) use `heliox:profile`; for the surrounding workspace (org name, members) use `heliox:workspace`; for executing restarts and the self-edit lifecycle (reflect, dream, changelog, restart) use `heliox:evolve`.

## Status

```bash
heliox status --json
heliox status --format text
```

`status --json` reports runtime id and brain fragment hashes/sizes for `base.md`, `soul.md`, `act.md`, `agents.md`, and `voice.md`, plus evolution changelog/reflection counts.

Use it before self-edit or restart work — it answers "is the brain in the state I expect?" and "did the previous restart land cleanly?".

## Restart preflight

Decide whether a restart is needed by inspecting `status` and recent changelog. The actual `heliox restart` command and its exit-code semantics live in `heliox:evolve`. Do not restart casually; restart budget is finite and exhaustion blocks self-edits until reset.

Rule of thumb: if you only edited `wiki/**`, `evolution/**`, or `plugins/**`, no restart is needed. Anything that changes `settings.json`, `soul.md`, `agents.md`, or `voice.md` requires a restart — see `heliox:evolve` for the command.
