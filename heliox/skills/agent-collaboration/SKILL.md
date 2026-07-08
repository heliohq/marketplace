---
name: agent-collaboration
description: "Deprecated alias — renamed to channel-charter-creator. Kept one release so existing brain files that still reference heliox:agent-collaboration keep resolving. On load, immediately use heliox:channel-charter-creator instead; do not select this skill for new work."
user-invocable: false
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox channel --help"
---

# Agent Collaboration (Deprecated)

This skill was renamed to **channel-charter-creator** in plugin 0.2.5. Stop and
load `heliox:channel-charter-creator` now — it owns all of the former protocol
content; none of it lives here. This alias exists only so brain files written
before the rename keep resolving, and it will be removed in the next plugin
release once templates reseed `base.md`/`act.md`.
