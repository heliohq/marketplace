#!/usr/bin/env python3
"""Drive `claude mcp login <server> --no-browser` for a headless agent.

WHY THIS EXISTS
  Claude Code's `mcp login --no-browser` prints the OAuth authorize URL and then
  reads the pasted redirect URL from STDIN — but it checks `isatty(stdin)` and
  refuses to run when stdin is not a real terminal (which is always the case for
  an agent shelling out). This wrapper runs it under a pseudo-terminal (pty) so
  it believes it has a TTY, captures the authorize URL to a file, and feeds the
  pasted callback URL back in when it appears.

USAGE (from the figma connect skill — see ../claude-code.md)
  1. Start it in the background:
       nohup python3 mcp_login_pty.py plugin:figma:figma \
            /tmp/figma_login.out /tmp/figma_callback.txt >/dev/null 2>&1 &
       sleep 12
  2. Read the authorize URL it captured, and relay it to the user:
       grep -oE 'https://www\\.figma\\.com/oauth[^ ]*' /tmp/figma_login.out | head -1
  3. When the user pastes the callback URL back (http://localhost:.../callback?code=...&state=...),
     write it to the callback file — the wrapper feeds it into the login and the
     exchange completes:
       printf '%s' '<pasted-callback-url>' > /tmp/figma_callback.txt
  4. Verify:  claude mcp list   (the figma row should show Connected)

ARGS
  argv[1]  MCP server name        (get the exact name from `claude mcp list`;
                                    for the official figma plugin it is
                                    `plugin:figma:figma`)
  argv[2]  output/log file        (default /tmp/figma_login.out)
  argv[3]  callback-url input file (default /tmp/figma_callback.txt)

Times out after 30 minutes.
"""

import os
import pty
import select
import sys
import time

server = sys.argv[1] if len(sys.argv) > 1 else "plugin:figma:figma"
out_path = sys.argv[2] if len(sys.argv) > 2 else "/tmp/figma_login.out"
cb_path = sys.argv[3] if len(sys.argv) > 3 else "/tmp/figma_callback.txt"

open(out_path, "w").close()
if os.path.exists(cb_path):
    os.remove(cb_path)

pid, fd = pty.fork()
if pid == 0:  # child: the actual login, under a TTY
    try:
        os.execvp("claude", ["claude", "mcp", "login", server, "--no-browser"])
    except OSError:
        os._exit(127)  # exec failed (claude not on PATH) — parent sees child exit

sent = False
start = time.time()
while True:
    try:
        wpid, _ = os.waitpid(pid, os.WNOHANG)
        if wpid == pid:  # login finished — drain any trailing output
            while True:
                r, _, _ = select.select([fd], [], [], 0.2)
                if not r:
                    break
                try:
                    d = os.read(fd, 4096)
                except OSError:
                    break
                if not d:
                    break
                with open(out_path, "ab") as f:
                    f.write(d)
            break
    except ChildProcessError:
        break

    r, _, _ = select.select([fd], [], [], 0.5)
    if r:
        try:
            d = os.read(fd, 4096)
        except OSError:
            break
        if d:
            with open(out_path, "ab") as f:
                f.write(d)

    if not sent and os.path.exists(cb_path):
        url = open(cb_path).read().strip()
        if url:
            os.write(fd, (url + "\n").encode())
            sent = True

    if time.time() - start > 1800:
        break

with open(out_path, "ab") as f:
    f.write(b"\n===LOGIN-PROCESS-EXITED===\n")
