---
name: memory
description: "Use `heliox memory ...` when prior memory may change the answer: user preferences, earlier decisions, recent agent activity, facts from another channel/entity, or a thin injected memory block. Trigger before re-asking, repeating work, or answering from uncertain recollection."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox memory --help"
---

# Heliox Memory

Look memory up before re-asking, repeating work, or answering from uncertain
recollection — when injected memory is thin, the user references prior context,
or you are about to repeat a decision.

## Model

Three verbs, one scope choice.

- `recall "<query>"` — search by topic / phrase / person / decision. Your default.
- `list` — newest entries in a scope (the user wants "latest", or you want to see what's stored before querying).
- `show <id>` — fetch one memory by id; do this before citing one as evidence.

Scope is picked first and applies to both `list` and `recall`:

- **omit `--app-id`** — the backend's default visible scope.
- **`--app-id self`** — this assistant's own activity lane; use it when the user asks what you recently did, said, checked, or handled elsewhere.
- **`--app-id "$APP_ID"`** — only when you already know the exact channel / entity / org / agent appId to bound the lookup.

Prefer `--json` (ids, scores, sources, metadata). In `recall`, use the user's
own phrasing — never prepend synthetic labels like `Message from ...`.

```bash
heliox memory recall "Yinuo prefers terse updates" --limit 20 --json
heliox memory recall "what did I work on recently?" --app-id self --limit 20 --json
heliox memory list --status active --limit 20 --json     # --status active|archived; --offset N to page
heliox memory show <id> --json
```

## Traps

- **Nothing found** → sharpen the query before widening scope. Still nothing → say "memory didn't surface it" and work from current context; never confabulate.
- **`--app-id "$APP_ID"` fails (auth / not-found)** → do not retry unchanged: verify the appId, or fall back to default scope only if that still answers the question.
- **Results conflict** → prefer the more specific scope, and `show` the memory before treating it as evidence.
