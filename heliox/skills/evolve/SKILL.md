---
name: evolve
description: "Use `heliox evolve ...` and `heliox restart ...` for AI self-improvement actions: reflection, dream delegation, waiting for dream sentinels, appending evolution changelog entries, and executing pod restarts after supported .brain edits. Trigger when the assistant is asked to improve its own behavior, install/update its brain, reflect on repeated mistakes, apply self-edits, or actually issue a restart. For deciding whether a restart is needed (status / brain-fragment preflight), use `heliox:status` first."
user-invocable: false
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox evolve --help"
---

# Heliox Evolve

Start by reading `../shared/SKILL.md`.

Use this for assistant self-improvement and `.brain` lifecycle actions.

## Reflect

Reflection is read-only:

```bash
heliox evolve reflect --reason "<why>" --json
heliox evolve reflect --reason "<why>" --scope soul|act|agents|all --json
```

It returns relevant fragments, recent changelog entries, and next steps.

## Dream

Dream delegates deeper reflection to a solo coding session and returns immediately:

```bash
heliox evolve dream --reason "<why>" --dedupe-key "<stable_trigger_id>" --json
```

Optional:

```bash
heliox evolve dream --reason "<why>" --source channel|scheduled|manual --dedupe-key "<id>" --dedupe-ttl 60 --json
```

The JSON result includes `run_id`, `channel_id`, `sentinel_path`, `launch_message`, and `deduplicated`.

Use a stable `--dedupe-key`, usually the triggering message id or schedule id, so repeated turns do not spawn duplicate dream sessions.

## Wait for Dream completion

```bash
heliox evolve wait-sentinel --sentinel-path <path> --run-id <run_id> --timeout 15m --json
```

Exit codes:

| Code | Meaning |
| --- | --- |
| 0 | sentinel ready |
| 10 | timeout |
| 11 | malformed sentinel or run_id mismatch |

On timeout, do not relaunch automatically. Report the timeout and let the next turn continue if needed.

## Changelog

Every self-edit must be logged:

```bash
heliox evolve changelog append --files "agents.md,voice.md" --why "<why>" --restart-reason "<reason>" --json
heliox evolve changelog show --limit 5 --json
heliox evolve changelog path
```

`--files` is comma-separated and refers to files under `~/.brain`.

## Restart

Before restarting, run `heliox status` to confirm the brain is in the expected state and inspect recent changelog (see `heliox:status` for status and the preflight rule of thumb). Then:

```bash
heliox restart --reason "<reason>" --json
heliox restart --reason "<reason>" --wait --json
```

Restart is needed for `settings.json`, `soul.md`, `agents.md`, and `voice.md`.

Restart is not needed for `wiki/**`, `evolution/**`, or `plugins/**`.

Exit code hints:

- `10`: restart budget exhausted; inspect the response recommendation and do not loop.
- `11`: actor indeterminate; runtime auth is misconfigured.
- `1`: other server or preflight failure.

## Guardrails

- Never edit `base.md` or `act.md` from inside a running assistant self-edit flow.
- Read `agents.md` before proposing or applying self-edits; it defines protected files and policy.
- Log changelog before restart when a restart will be triggered.
