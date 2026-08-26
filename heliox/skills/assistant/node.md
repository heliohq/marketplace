# Heliox Assistant Nodes

`heliox assistant node ...` inspects the runtime hosts an assistant can spawn
on: Helio cloud clusters, org-managed nodes, or a user's private local device.
Use it when an assistant needs a specific host, or to fill
`heliox assistant create --node`.

## List nodes

```bash
heliox assistant node list --json
```

Each row carries the node's `id`, `kind`, `status`, `scope`, `display_name`,
a `host_cli` probe summary (`{"claude": "found", ...}`; statuses are
`found` / `not_found` / `unknown`; `found` means `--provider host` is viable
there for that engine), and `active_runtimes`. Pass the node id to
`heliox assistant create --node <node_id>` when the user wants a specific
runtime host.

A **host-provider** assistant (`--provider host`, using the node's own
claude/codex CLI login) runs on a **local node only**: pass `--node
<local-node-id>` for a node where the user has already logged in to the target
engine. `--node` only chooses where the runtime spawns; it does not select the
model provider (that is `--provider`).

## Adding a node

Pairing a new device as a runtime node (installing the local daemon and
registering it) is a desktop flow, not a CLI one. `heliox assistant node create`
returns guidance with a deep link to the desktop Settings → Devices panel; relay
that link to the user.
