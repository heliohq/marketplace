---
name: memory
description: "Use `heliox memory ...` for durable per-AI memory across turns and context compaction. Trigger when the assistant needs to inspect, search, add, update, or archive channel-anchored memory."
user-invocable: false
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox memory --help"
---

# Heliox Memory

Start by reading `../shared/SKILL.md`.

Memory is persistent semantic storage owned by one AI user and anchored to Helio channels. It survives pod restarts and context compaction.

## When to write

Write a memory when:

- The user corrects you.
- You see the same convention twice.
- A non-obvious decision was made and the reasoning will matter later.
- A long task may outlive current context.

Do not store trivia, visible-in-code facts, or transient task state.

## Content

Memory no longer has Helio product-level `channel` or `user` types. Write the "who did what" context directly in the memory content, and always anchor the write/read with `--channel-id`.

## Commands

```bash
heliox memory add "<content>" --channel-id "$CHANNEL_ID" --message-id "$MESSAGE_ID" --json
heliox memory add "Yinuo prefers concise status updates." --channel-id "$CHANNEL_ID" --message-id "$MESSAGE_ID" --json
heliox memory list --json
heliox memory list --status active --limit 20 --json
heliox memory search "<query>" --channel-id "$CHANNEL_ID" --limit 20 --json
heliox memory search "<query>" --channel-id "$CHANNEL_ID" --json
heliox memory show <id> --json
heliox memory update <id> "<new content>" --json
heliox memory delete <id> --yes --json
```

## Context compaction

For long multi-step work, store one channel memory with the durable goal and key inputs. Future turns can recover by searching memory and channel history.
