---
name: memory
description: "Use `heliox memory ...` when prior memory may change the answer: user preferences, earlier decisions, recent agent activity, facts from another channel/entity, or a thin injected memory block. Trigger before re-asking, repeating work, or answering from uncertain recollection."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox memory --help"
---

# Heliox Memory

Use this skill for memory lookup and inspection.

## Current model

- `list` returns newest memories in a visible scope.
- `recall` searches memories in the same visible scope by query.
- `show` fetches one memory by id after `list` or `recall` finds it.
- `list` and `recall` share the same scope rules. Choose the scope first, then choose whether you need newest entries (`list`) or query-ranked entries (`recall`).
- Omit `--app-id` for the backend's default visible scope.
- Use `--app-id self` for this assistant's own activity lane, especially when the user asks what you recently did, said, checked, or handled elsewhere.
- Use `--app-id "$APP_ID"` only when you already know the exact channel, entity, org, or agent appId that should bound the lookup.
- Prefer `--json` for assistant-facing operations so ids, scores, sources, and metadata are easy to inspect.

## Recommended lookup path

1. Decide whether memory is needed: use it when injected memory is incomplete, the user references prior context, or you are about to repeat a decision or ask a question that memory may already answer.
2. Pick the scope: default visible scope, `--app-id self`, or a known exact `--app-id "$APP_ID"`.
3. Use `recall` when you have a topic, phrase, person, task, file, or decision to search for.
4. Use `list` when the user asks for latest memory, recent activity, or you need to inspect what is stored before deciding a query.
5. If a result is ambiguous, run `heliox memory show <id> --json` before treating it as evidence.
6. If no relevant memory appears, say memory did not surface it instead of pretending to remember.

## Commands

### List

```bash
heliox memory list --json
heliox memory list --status active --limit 20 --json
heliox memory list --status active --limit 20 --offset 20 --json
heliox memory list --status archived --limit 20 --json
heliox memory list --app-id self --limit 20 --json
heliox memory list --app-id "$APP_ID" --limit 20 --json
```

`--status` accepts `active` or `archived`. `--offset` is for pagination. Start with `--limit 10` or `--limit 20`; increase only if the result set is thin.

### Recall

```bash
heliox memory recall "Yinuo prefers update style" --limit 20 --json
heliox memory recall "what did I work on recently?" --app-id self --limit 20 --json
heliox memory recall "<query>" --app-id "$APP_ID" --limit 20 --json
```

Use the user's original phrasing when possible. Do not prepend synthetic labels like `Message from ...`; the query should be the actual topic or text you need memory for.

### Show

```bash
heliox memory show <id> --json
```

Use `show` for a specific id returned by `list` or `recall`, especially before citing a memory in a user-facing answer.

## Failure handling

- If default-scope recall returns nothing, try a sharper query before widening scope.
- If the user asks about this assistant's recent activity, use `--app-id self` rather than guessing from channel memory.
- If an exact `--app-id "$APP_ID"` fails with an authorization or not-found error, do not retry the same command unchanged. Verify the appId or fall back to the default visible scope only if that still matches the user's question.
- If results conflict, prefer the more specific scope and inspect the memory with `show`.
- If memory still does not answer the question, say so and proceed from the current context.

## Ready patterns

```bash
heliox memory recall "<topic from the user>" --limit 20 --json
```

```bash
heliox memory list --app-id self --limit 20 --json
heliox memory recall "recent activity related to <topic>" --app-id self --limit 20 --json
```

```bash
heliox memory list --app-id "$APP_ID" --limit 20 --json
heliox memory recall "<topic>" --app-id "$APP_ID" --limit 20 --json
heliox memory show <id> --json
```
