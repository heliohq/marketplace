# Figma (official MCP — install the official plugin, then authenticate)

Read [../SKILL.md](../SKILL.md) first for the general connected-tools model, but
Figma is a **special case**: it is the **official Figma MCP server**
(`https://mcp.figma.com/mcp`), not an AnyCLI REST tool. You do **not** run
`heliox tool figma -- <args>`. You connect it once, then call its tools directly.

Why MCP: the official server gives full design context (`get_design_context`,
`get_metadata`, `get_screenshot`, `get_variable_defs`, `get_figjam`) **and**
canvas writes (`use_figma`, `generate_figma_design`, `create_new_file`,
`upload_assets`) — none of which the Figma REST API exposes.

## The model (same for both engines)

Figma ships as the **official `figma` plugin** in the plugin marketplace. That
plugin **registers the Figma MCP server for you** — so connecting is:

1. **Check first** — is Figma already connected? If yes, stop (don't reinstall).
2. **Install the official plugin with your ENGINE's own plugin command** — this
   registers the Figma MCP server. Do **NOT** manually `mcp add` (that duplicates
   what the plugin does and conflicts).
3. **Authenticate** — the Figma MCP uses OAuth: you produce an authorize URL,
   relay it to the user, they authorize and paste the callback URL back, you
   complete the exchange.

The install command + auth mechanics differ per engine. Read your engine's file
(`HELIO_RUNTIME_HARNESS` tells you which):

- `claude-code` → [claude-code.md](./claude-code.md)
- `codex` → [codex.md](./codex.md)

```bash
echo "$HELIO_RUNTIME_HARNESS"   # claude-code | codex
```

## Safety

- **Never echo tokens.** The user pastes back a **callback URL** (carries a
  one-time `code`), never an access token. The exchange happens inside the CLI.
- Validate the callback's `state` matches the authorize URL before completing.
- Canvas writes (`use_figma`, `create_new_file`, …) are outward-facing edits to
  the user's Figma files — follow the sensitive-operation rule in
  [../SKILL.md](../SKILL.md) before writing.
