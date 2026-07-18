# Figma connect — Claude Code engine

Read [figma.md](./figma.md) first. This is the `HELIO_RUNTIME_HARNESS=claude-code`
path. You install the official Figma plugin (which registers the Figma MCP
server), then authenticate with `claude mcp login`.

> **Why not the `mcp__figma__*` in-session tools?** The plugin's MCP tools
> (`mcp__figma__authenticate`, `mcp__figma__whoami`, …) only load at Claude
> **session startup**. When you install the plugin mid-session they do NOT become
> callable this turn (or after a wakeup). So do **not** rely on them to connect —
> drive `claude mcp login` below instead. Those tools become available for the
> real Figma work in a later session, once the credentials are stored.

## Step 0 — check first (skip if already connected)

Connected = the Figma MCP tools work in your session — if you already have them, STOP.
`claude mcp list` also reports real state, so it's a valid check too:

```bash
claude mcp list        # figma row (server `plugin:figma:figma`) shows "Connected" → done, STOP
```

## Step 1 — install the official Figma plugin

```bash
claude plugin install figma@claude-plugins-official
```

Registers the Figma MCP server (named `plugin:figma:figma`). If it says "already
installed", that's fine. Do **not** `mcp add` and do **not** `heliox plugin`.

## Step 2 — authenticate (one turn) via the pty login helper

`claude mcp login --no-browser` prints the authorize URL and reads the pasted
callback from stdin — but it requires a real TTY, which an agent shell is not.
Use the bundled pty wrapper (locate it; it is projected with this skill). It is
POSIX-only (Python `pty`, so darwin/linux — `HELIO_RUNTIME_PLATFORM_OS`); a
Windows local runtime needs a different TTY shim:

```bash
LOGIN=$(find / -path '*tool/figma/scripts/mcp_login_pty.py' 2>/dev/null | head -1)
```

1. **Record position**: `heliox message list --json | head` → note latest id → `<SEQ>`.
2. **Start the login helper** (background; it captures the URL and waits for the callback):
   ```bash
   nohup python3 "$LOGIN" plugin:figma:figma /tmp/figma_login.out /tmp/figma_callback.txt >/dev/null 2>&1 &
   sleep 12
   ```
3. **Read the authorize URL** it captured:
   ```bash
   grep -oE 'https://www\.figma\.com/oauth[^ ]*' /tmp/figma_login.out | head -1   # keep its state=
   ```
4. **Relay to the user**:
   ```bash
   heliox message send '<#channel|@user>' 'To connect Figma, open this and click Allow: <URL>. If that page then shows an error or does not load, that is expected — copy the FULL URL from your browser address bar and paste it back here.' --seen <SEQ>
   ```
5. **Wait in this turn** — poll every 3s, up to **3 minutes**, for the reply
   containing a `…/callback?code=…&state=…` URL (verify `state` matches Step 3):
   ```bash
   heliox message list --after <SEQ> --json   # repeat every 3s
   ```
6. **Complete** — hand the pasted callback to the waiting login helper:
   ```bash
   printf '%s' '<pasted-callback-url>' > /tmp/figma_callback.txt
   sleep 3
   ```
7. **Verify + confirm**:
   ```bash
   claude mcp list   # figma → Connected
   ```
   `heliox message send` "Figma is connected." The `mcp__figma__*` tools become
   available in your next session; credentials persist.

## Local-node shortcut

On a **local** runtime (the assistant runs on the user's own machine) the
`localhost:3118` callback in the URL is reachable, so authorizing in the browser
often **auto-completes** the login — no paste-back needed. Still poll `claude mcp
list` for `Connected`; only fall back to the paste-back (step 6) if it stalls.

## Timeout

If 3 minutes pass with no callback and `claude mcp list` still isn't Connected:
`pkill -f 'mcp_login_pty'`, `heliox message send` a retry note, and end the turn.

## Footguns

- **Don't wait for `mcp__figma__authenticate`** — it isn't loaded this session.
  Authenticate via `claude mcp login` (the pty helper), not the in-session tools.
- **Don't `mcp add figma`** — the plugin already registers the Figma MCP.
- The exact server name is `plugin:figma:figma` (confirm with `claude mcp list`),
  not bare `figma`.
- The user pastes a **callback URL**, not a token — never echo or log tokens.
