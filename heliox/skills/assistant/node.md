# Heliox Assistant Nodes

`heliox assistant node ...` inspects the runtime hosts an assistant can spawn
on: Helio cloud clusters, org-managed nodes, or a user's private local device.
Use it when an assistant needs a specific host, or to fill
`heliox assistant create --node`.

## List nodes

```bash
heliox assistant node list --json
```

The JSON includes each node's id, kind, status, owner scope, display name, and
device id. Pass the node id to `heliox assistant create --node <node_id>` when
the user wants a specific runtime host.

A **host-provider** assistant (`--provider host`, using the node's own
claude/codex CLI login) runs on a **local node only** — pass `--node
<local-node-id>` for a node where the user has already logged in to the target
engine. `--node` only chooses where the runtime spawns; it does not select the
model provider (that is `--provider`).

## Adding a node

Pairing a new device as a runtime node (installing the local daemon and
registering it) is a desktop flow, not a CLI one. `heliox assistant node create`
returns guidance with a deep link to the desktop Settings → Devices panel; relay
that link to the user.
