# Figma connect: Codex engine

Read [figma.md](./figma.md) first. This is the `HELIO_RUNTIME_HARNESS=codex`
path. You install the official Figma plugin (which registers the Figma MCP
server), then authenticate with `codex mcp login`.

## Step 0: check first (skip if already connected)

Connected = the Figma MCP tools actually work in your session. If you already have
Figma MCP tools (or a trivial call succeeds), STOP. Don't use `codex mcp list`; it's
config-only (a `figma enabled/OAuth` row shows even when logged out).

## Step 1: install the official Figma plugin

```bash
codex plugin add figma@claude-plugins-official
```

If that reports the marketplace is missing, register it first, then retry:

```bash
codex plugin marketplace add anthropics/claude-plugins-official
```

This registers the Figma MCP server (`codex mcp list` will then show a `figma`
row). Always pass `@<marketplace>`: `codex plugin add figma` alone errors when
figma exists in more than one marketplace. Do **not** `mcp add`.

## Step 2: authenticate (one turn)

1. **Record position**: `heliox message list --json | head` → note latest seq → `<SEQ>`.
2. **Start login detached** (it binds a loopback listener and blocks; `nohup … &`
   keeps it alive without hanging this turn, and on a local node stops it from
   blocking on an opened browser). Commands below assume a POSIX shell
   (`HELIO_RUNTIME_PLATFORM_OS` = darwin/linux); on Windows drive `codex mcp login
   figma` through your shell's own background/redirect and paste-back equivalent:
   ```bash
   rm -f /tmp/figma-login.log
   nohup bash -c 'codex mcp login figma >/tmp/figma-login.log 2>&1' </dev/null >/dev/null 2>&1 &
   sleep 12
   ```
3. **Read the URL + loopback endpoint** from the log:
   ```bash
   grep -oE 'https://www\.figma\.com/oauth[^ ]*' /tmp/figma-login.log | head -1   # authorize URL (keep its state=)
   # the redirect_uri in that URL is the loopback to POST the callback to, e.g.
   #   http://127.0.0.1:<port>/callback/<path>
   ```
4. **Relay to the user**:
   ```bash
   heliox message send '<#channel|@user>' 'To connect Figma, open this and click Allow: <URL>. If that page then shows an error or does not load, that is expected. Copy the FULL URL from your browser address bar and paste it back here.' --seen <SEQ>
   ```
5. **Wait in this turn**: poll every 3s, up to **3 minutes**, for the reply with
   `…?code=…&state=…` (verify `state` matches Step 3):
   ```bash
   heliox message list --after <SEQ> --json   # repeat every 3s
   ```
6. **Complete**. POST the pasted callback to the detached login's loopback:
   ```bash
   curl -s "http://127.0.0.1:<port>/callback/<path>?code=<CODE>&state=<STATE>"
   ```
7. **Verify + confirm**: rely on the login exiting 0 (loopback callback returned),
   not `codex mcp list`. Figma tools appear next session; `heliox message send`
   "Figma is connected."

## Timeout

If 3 minutes pass with no callback: `pkill -f 'codex mcp login'`, then
`heliox message send` a retry note, and end the turn.

## Footguns

- **The login must be detached (`nohup … &`).** A foreground `codex mcp login`
  blocks the whole turn; on a local (mac) node it also opens a browser and hangs.
  Detached, it prints the URL to the log and you drive the paste-back instead.
  (Do NOT use `setsid`: it is absent on macOS.)
- **Do not `mcp add figma`**: the plugin already registers the Figma MCP.
- The user pastes a **callback URL**, not a token; never echo or log tokens.
- Codex stores the token (with a refresh token) under `~/.codex`; it persists and
  refreshes silently, so this connect is one-time.
