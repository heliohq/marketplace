---
name: node
description: "Use `heliox node ...` to inspect runtime hosts available for assistant creation, especially when choosing a local BYOA node, checking cloud/local capacity, or filling `heliox assistant create --node`."
user-invocable: false
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox node --help"
---

# Heliox Node

Start by reading `../shared/SKILL.md`.

Nodes are runtime hosts: Helio cloud clusters, org-managed nodes, or a user's
private local device. Use this surface when an assistant needs to be created on
a specific host or when a user asks what runtime hosts are available.

## List nodes

```bash
heliox node list --json
```

The JSON includes each node's id, kind, status, owner scope, display name, and
device id. Pass the node id to `heliox assistant create --node <node_id>` when
the user wants a specific runtime host.

For BYOA assistants, pair `--node` with `--auth-mode=byoa`; the node must be a
local host where the user has already logged in to the target engine.
