# Browser (`heliox tool browser -- ...`)

Read [../SKILL.md](../SKILL.md) first for the general model — but note browser
is the **odd one out**: it is *not* an OAuth-connected account. It drives a
browser the user **paired** with you — their own local Chrome, with their real
login state (SSO, sessions, cookies). There is no cloud browser and no
self-launched fallback: if no paired browser is online, the tool fails fast
with a clear error instead of downgrading to a throwaway browser with none of
the user's login state.

Everything after `--` is passed to the underlying `agent-browser` CLI
verbatim. heliox picks the paired browser and injects an authenticated
connection automatically — you never handle endpoints or tokens.

```bash
heliox tool browser [--browser <name|id>] -- <agent-browser args...>
```

## When to use the browser (vs WebSearch)

Reach for the browser when the task needs **the user's own login state or an
action on a site** — reading a private dashboard, posting/buying/filling a form,
acting inside Gmail/LinkedIn/X while signed in, anything that only works because
it's *their* logged-in Chrome. That real login state is the entire reason this
tool exists.

For **public open-web research** where no login is needed, prefer **WebSearch /
WebFetch** — they're faster, more robust, don't consume the user's browser, and
don't trip anti-bot defenses. Don't open a search engine in the browser to look
something up; search directly.

## Discover and pair

```bash
heliox tool browser list                 # paired browsers + online state
heliox tool browser connect              # mint a connect link (pairing onboarding)
heliox tool browser connect '#channel'   # target the completion event elsewhere
heliox tool browser connect '@user'      # target a specific user
```

- `no_paired_browser` → run `connect`, then weave the link into a plain
  message to the user in your own words. A system message wakes you when they
  finish — do not poll.
- `browser_offline` → the paired browser's Chrome isn't running; message the
  user and ask them to open Chrome.
- Several browsers online (`ambiguous_browser`) → pick one explicitly with
  `--browser <name|id>`. Omit `--browser` when exactly one is online — the
  server picks it.

## Read and act

Open the page, snapshot to get refs, then act on refs:

```bash
heliox tool browser -- open <url>
heliox tool browser -- snapshot
heliox tool browser -- click <ref_or_selector>
heliox tool browser -- fill <ref_or_selector> "<value>"
heliox tool browser -- type <ref_or_selector> "<text>"
heliox tool browser -- press <key>
heliox tool browser -- wait <ref_or_selector_or_ms>
heliox tool browser --browser "Work Chrome" -- open <url>   # explicit browser
```

Prefer accessibility refs such as `@e5` from `snapshot`. CSS selectors are a
fallback. `fill` clears and fills; `type` appends using real keystrokes.

**`open` timing out is usually NOT a failure.** Many modern sites (x.com,
YouTube, lots of SPAs) stream or poll forever and never fire the page `load`
event, so `open` prints `✗ page.goto: Timeout … waiting until "load"` even
though the page **loaded fine and is fully interactive**. Do **not** close and
reopen in a loop — that wastes the turn and gets nowhere. Instead just proceed:
run `get url` / `snapshot` to confirm the page is there (it will be) and keep
going. If you need a specific element to be ready first, chain a short
`wait "<selector>"` or `wait --text "<text>"` rather than relying on `load`.

## Get page data, screenshots, JavaScript

```bash
heliox tool browser -- get url
heliox tool browser -- get title
heliox tool browser -- get text [ref_or_selector]
heliox tool browser -- get html [ref_or_selector]
heliox tool browser -- screenshot ./out.png
heliox tool browser -- eval "document.title"
```

Screenshot before high-risk clicks. Use `eval` sparingly; prefer the
accessibility snapshot and normal browser commands.

## Working in the user's browser

- You are operating the user's real Chrome. Your tabs live in a tab group
  named after you, and the page shows a "Helio is working" indicator — the
  user can see and interrupt everything you do.
- **Your workspace persists across commands.** The open pages, tabs, and their
  state stay alive between calls (and survive brief drops), so a later command
  lands on the same pages you left — reuse is automatic; you don't re-open from
  scratch each time. The workspace is torn down only on explicit close, ~30 min
  with no browser command, or the browser going offline.
- If a page needs the human (login prompt, 2FA, captcha, an anti-bot
  "solve the challenge" / "you've been blocked" wall, or a redirect to a login
  page), **stop automating and message the user in the channel** — say which tab
  needs them. It's their browser and they're right there: they clear it directly
  on the page and reply, then you continue. There is no takeover hand-off to
  perform. **Do not retry-churn** (close+reopen, hammer the URL) against a wall —
  it won't clear it and burns the turn.
- Aggressive-anti-bot consumer sites (X, Reddit, logged-out LinkedIn, Google
  search) may serve a challenge *intermittently* even on the user's own
  logged-in Chrome — this is expected, not a bug in the tool. For pure research
  on such sites, prefer WebSearch; when the task genuinely needs the site, hand
  the challenge to the co-present user as above.
- Your tabs are a temporary workspace: deliver results through channel
  messages/files, not by leaving tabs open.

## Flags that don't apply here

You are driving the user's paired Chrome over an injected `--cdp` session, not a
browser agent-browser launched itself. So **ignore** the agent-browser features
that assume a self-managed browser — heliox handles connection and identity for
you, and some of these would disrupt the user's real Chrome:

- `connect` / `--cdp` / `--auto-connect` — heliox already connected you.
- `--profile`, `state save` / `state load`, the auth vault — the user's real
  profile *is* the login state; don't try to save/load/swap it.
- `--headed` — it's already a visible, real browser window.
- `close --all` — never; it acts on the user's browser. `close` is rarely
  needed at all (your workspace is meant to persist between commands).

Just use the page and interaction commands (open / snapshot / click / fill /
type / get / wait / screenshot / eval).

## Safety

- Outward-facing actions in the user's real, logged-in browser (submitting
  forms, sending messages, making purchases, anything that mutates a live
  account) follow the sensitive-operation rule from `../shared/SKILL.md` —
  confirm before acting unless already authorized.
- The injected CDP endpoint *is* the credential; heliox redacts it from
  passthrough output. Never try to reconstruct, log, or echo it.
