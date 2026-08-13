---
name: document
description: "Use `heliox document ...` for Helio collaborative documents: read a live document as markdown, make exact in-place text edits, or handle `helio://document/<id>` references. Trigger when the user asks to inspect or edit a Helio document, task-description document, or document URI."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox document --help"
---

# Heliox Document

`heliox document` is the AI-facing surface for Helio collaborative documents.
It connects to the live Yjs document as a peer, so reads and edits see the same
state humans see in the editor.

## Read

```bash
heliox document read <id>
heliox document read helio://document/<id>
heliox document read <id> --json
```

Read before editing. The output is markdown rendered for an agent, with line
numbers for orientation. Line numbers are not edit anchors.

`--json` returns the document envelope instead: metadata plus `routeUrl` and
`markdown`. `routeUrl` is the canonical URI to paste when linking the document
in a message — never hand-assemble a `helio://` link.

`heliox blob get helio://document/<id>` redirects to the same rendered read
path, but prefer `document read` when the thing is plainly a document.

## Edit

```bash
heliox document edit <id> --old "exact text" --new "replacement text"
heliox document edit helio://document/<id> --old "exact text" --new "replacement text"
heliox document edit <id> --old "repeated text" --new "replacement" --replace-all
```

`--old` matches contiguous plain text in the live document. Without
`--replace-all`, the match must be unique. If it is missing or ambiguous, read
the document again and choose a more precise span.

## Share

To point a human at a document in a message, write `[<document title>](helio://document/<id>)` — the title as link text, the document's canonical URI as the target. Use a URI you already hold (`create --json` returns it as `routeUrl`; read/edit targets are already this form) — never guess an id. It renders as a titled chip that opens the document in-app. A bare `helio://document/<id>` also renders as a clickable chip, but shows the raw URI instead of the title — prefer the titled form. Inside Helio messages `routeUrl` is the canonical share form; don't hand-build an `https://…` web URL for a document.

## Search

```bash
heliox document search "<query>"
```

Cross-document search is currently a placeholder and returns an explicit
not-implemented error. For now, read the target document and search the rendered
markdown locally.

## Safety

- Do not rewrite a whole document when a targeted edit works.
- Do not use line numbers as edit coordinates; use exact text spans.
- If a human may be editing concurrently, keep changes small and re-read after
  a contested edit.
