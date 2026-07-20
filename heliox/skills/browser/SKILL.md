---
name: browser
description: "Use `heliox tool browser ...` for any web-page interaction the assistant needs to perform: opening URLs, login / accept-invite flows, clicking, filling forms, reading SPA content (JS-rendered pages where curl returns nothing useful), taking screenshots, running ad-hoc JavaScript, and closing the session. Trigger whenever the task involves visiting or interacting with a website — this is the only browser surface available to AI runtimes; the assistant has no other way to drive a real Chrome / accept invitations / log into a third-party app."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox tool browser --help"
---

# Heliox Browser

Start by reading `../shared/SKILL.md`.

Use this for a Hyperbrowser-managed cloud Chrome session. There is one active session per AI user.

## Lifecycle

```bash
heliox tool browser open <url> --json
heliox tool browser open <url> --timeout-minutes 30 --stealth --json
heliox tool browser close --json
```

Close the session when done. Idle sessions consume browser quota.

## Read and act

Open the page, snapshot to get refs, then act on refs:

```bash
heliox tool browser snapshot --json
heliox tool browser snapshot ./snapshot.txt
heliox tool browser click <ref_or_selector> --json
heliox tool browser fill <ref_or_selector> "<value>" --json
heliox tool browser type <ref_or_selector> "<text>" --json
heliox tool browser press <key> --json
heliox tool browser wait <ref_or_selector_or_ms> --json
```

Prefer accessibility refs such as `@e5` from `snapshot`. CSS selectors are a fallback.

`fill` clears and fills. `type` appends using real keystrokes.

## Get page data

```bash
heliox tool browser get url --json
heliox tool browser get title --json
heliox tool browser get text [ref_or_selector] --json
heliox tool browser get html [ref_or_selector] --json
heliox tool browser get value <ref_or_selector> --json
heliox tool browser get attr <attr_name> <ref_or_selector> --json
heliox tool browser get count <selector> --json
heliox tool browser get box <ref_or_selector> --json
heliox tool browser get styles <ref_or_selector> --json
```

Allowed `get` values are `text`, `html`, `value`, `attr`, `title`, `url`, `count`, `box`, and `styles`.

## Screenshot and JavaScript

```bash
heliox tool browser screenshot --json
heliox tool browser screenshot ./out.png --json
heliox tool browser eval "document.title" --json
```

Screenshot before high-risk clicks. Use `eval` sparingly; prefer the accessibility snapshot and normal browser commands.
