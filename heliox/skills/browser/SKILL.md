---
name: browser
description: "Use `heliox browser ...` for any web-page interaction the assistant needs to perform: opening URLs, login / accept-invite flows, clicking, filling forms, reading SPA content (JS-rendered pages where curl returns nothing useful), taking screenshots, running ad-hoc JavaScript, and closing the session. Trigger whenever the task involves visiting or interacting with a website — this is the only browser surface available to AI runtimes; the assistant has no other way to drive a real Chrome / accept invitations / log into a third-party app."
user-invocable: false
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox browser --help"
---

# Heliox Browser

Start by reading `../shared/SKILL.md`.

Use this for a Hyperbrowser-managed cloud Chrome session. There is one active session per AI user.

## Lifecycle

```bash
heliox browser open <url> --json
heliox browser open <url> --timeout-minutes 30 --stealth --json
heliox browser close --json
```

Close the session when done. Idle sessions consume browser quota.

## Read and act

Open the page, snapshot to get refs, then act on refs:

```bash
heliox browser snapshot --json
heliox browser snapshot --no-interactive --json
heliox browser click <ref_or_selector> --json
heliox browser fill <ref_or_selector> "<value>" --json
heliox browser type <ref_or_selector> "<text>" --json
heliox browser press <key> --json
heliox browser wait <ref_or_selector_or_ms> --json
```

Prefer accessibility refs such as `@e5` from `snapshot`. CSS selectors are a fallback.

`fill` clears and fills. `type` appends using real keystrokes.

## Get page data

```bash
heliox browser get url --json
heliox browser get title --json
heliox browser get text [ref_or_selector] --json
heliox browser get html [ref_or_selector] --json
heliox browser get value <ref_or_selector> --json
heliox browser get attr <attr_name> <ref_or_selector> --json
heliox browser get count <selector> --json
heliox browser get box <ref_or_selector> --json
heliox browser get styles <ref_or_selector> --json
```

Allowed `get` values are `text`, `html`, `value`, `attr`, `title`, `url`, `count`, `box`, and `styles`.

## Screenshot and JavaScript

```bash
heliox browser screenshot --json
heliox browser screenshot ./out.png --json
heliox browser eval "document.title" --json
```

Screenshot before high-risk clicks. Use `eval` sparingly; prefer the accessibility snapshot and normal browser commands.
