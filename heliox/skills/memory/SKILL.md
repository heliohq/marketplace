---
name: memory
description: "Use `heliox memory ...` for durable per-AI memory across turns and context compaction. Trigger when the assistant has been corrected, learns a recurring convention, discovers a trap, captures a decision, tracks current focus for a long task, searches prior durable knowledge, or needs to archive/report/update a memory."
user-invocable: false
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox memory --help"
---

# Heliox Memory

Start by reading `../shared/SKILL.md`.

Memory is persistent semantic storage scoped per AI user. It survives pod restarts and context compaction.

## When to write

Write a memory when:

- The user corrects you.
- You see the same convention twice.
- A non-obvious decision was made and the reasoning will matter later.
- A long task may outlive current context.

Do not store trivia, visible-in-code facts, or transient task state.

## Categories

| Category | Use |
| --- | --- |
| `convention` | "We always do X this way." |
| `trap` | "X looks right but breaks because Y." |
| `decision` | "We chose X over Y because Z." |
| `preference` | User-specific style or approach. |
| `current_focus` | What you are in the middle of. Decays naturally. |

## Commands

```bash
heliox memory add "<content>" --category convention --entities a,b,c --confidence 0.9 --json
heliox memory list --json
heliox memory list --category trap --status active --json
heliox memory search "<query>" --limit 5 --json
heliox memory show <id> --json
heliox memory update <id> "<new content>" --json
heliox memory reinforce <id> --json
heliox memory delete <id> --json
heliox memory restore <id> --json
heliox memory report <id> --reason no_longer_accurate --note "<context>" --json
heliox memory consolidate --json
heliox memory status --json
```

Report reasons:

- `no_longer_accurate`
- `misinterpreted`
- `too_generic`
- `just_wrong`
- `other`

## Context compaction

For long multi-step work, add one `current_focus` memory early with the goal and key inputs. Future turns can recover from compaction by searching memory and channel history.
