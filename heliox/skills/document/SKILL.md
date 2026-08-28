---
name: document
description: "Use `heliox document ...` for Helio collaborative documents: create a document with an initial markdown body, read a live document as markdown, make exact in-place text edits, or handle `helio://document/<id>` references. Trigger when the user asks to create, inspect, or edit a Helio document, task-description document, or document URI."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox document --help"
---

# Heliox Document

`heliox document` is the AI-facing surface for Helio collaborative documents.
It connects to the live Yjs document as a peer, so reads and edits see the same
state humans see in the editor.

## Create

```bash
heliox document create "<title>" --content "<markdown body>" --json
heliox document create "<title>" --content "<markdown body>" --channel '#engineering'
heliox document seed <id> --content "<markdown body>"     # first body of an existing empty document
```

Pass `--content` at create time: the server mints every document empty, and
`edit` cannot write a first body (`--old ""` is rejected, and an empty
document has no text to anchor on). `document seed` is the same first write
for a document that already exists empty, including the recovery path when
`create` reports the document was created but its content failed to seed.

`--channel` binds the document to a channel (`#name`) or a DM (`@handle`);
omit it for a standalone document. `--json` returns the envelope with the
`routeUrl` to share. This creates plain documents only: task-description and
automation documents are created by their parent entity (`task create`,
`automation create`), not here.

## Read

```bash
heliox document read <id>
heliox document read helio://document/<id>
heliox document read <id> --json
```

Read before editing. The output is the document's raw markdown: no line-number
gutter, nothing added. `heliox document read <id> > doc.md` gives you a file
you can treat as a plain `.md`, and `edit --old` matches those exact bytes.

`--json` returns the document envelope instead: metadata plus `routeUrl` and
`markdown`. `routeUrl` is the canonical app URL to paste when linking the document
in a message; never hand-assemble a `helio://` link.

`heliox blob get helio://document/<id>` redirects to the same rendered read
path, but prefer `document read` when the thing is plainly a document.

## Edit

```bash
heliox document edit <id> --old "exact text" --new "replacement text"
heliox document edit helio://document/<id> --old "exact text" --new "replacement text"
heliox document edit <id> --old "repeated text" --new "replacement" --replace-all
```

Edit the document exactly as you would edit a local `.md` file. `--old` and
`--new` are both markdown: `--old` matches the bytes `read` printed, and `--new`
is parsed as markdown. Without `--replace-all` the match must be unique; if it
is missing or ambiguous, read again and choose a more precise span.

A `note:` line on stderr is not a failure: the edit landed. It says a
`helio://` reference you wrote points at something that does not exist, which
usually means the id was assembled from memory rather than taken from a
`routeUrl` or a read/edit target. Fix it with another edit if it was yours; a
reference that was already in the document is not reported. A LOCAL file path
(`./shot.png`) is the one reference that does stop the write, because it
resolves only on this machine; upload it with `heliox blob put` and use the
printed `helio://attachment/<id>`.

Because the markup is part of the text, it is part of the edit:

```bash
# **身份**：产品经理
--old '身份'     --new '角色'   # → **角色**：产品经理   (bold stays)
--old '**身份**' --new '角色'   # → 角色：产品经理       (bold goes with the asterisks)
```

The same follows everywhere: `--old '# '` changes a heading level, `--old` may
span a blank line to match across paragraphs, and `--new '**x**'` writes bold.
Markup you did not touch is left alone, as are comment anchors, colours and
other things markdown cannot spell.

A value carrying `$` or backticks gets shell-mangled inside `"..."`: the shell
expands them before Helio ever sees the text. Documents hit this more often than
messages do: a fenced code block is backticks by definition, and `--old` must
match the document's bytes *exactly*, so a mangled anchor does not fail loudly,
it just stops matching. Don't hand-escape or drop the fence to dodge it; use
`--args-file` instead:

- Write the whole invocation as a JSON array to a file:
  `["document","edit","<id>","--old","…exact text…","--new","…replacement…"]`.
- Run `heliox --args-file <path>`, nothing else on the line.
- The array holds the **literal text**, never a path to a draft file in a value
  (`--old` / `--new` / `--content`): a future runtime can't read a file that
  only existed here.

`--args-file` is the exception, not the default. Multi-line spans, apostrophes,
markdown headings, `#`, `;`, `!`, `?`, and every non-ASCII script pass through
`"..."` byte-exact. Send them inline. Reaching for the transport on every edit
costs a file write and a second command for nothing.

## Share

To point a human at a document in a message, write `[<document title>](routeUrl)`: the title as link text and the `https://app.helio.im/document/...` value returned by `create --json` or `read --json` as the target. Never guess or hand-build an id. A bare `routeUrl` is clickable, but the titled form reads better. Legacy `helio://document/...` references remain valid inputs; do not emit them in a new message.

## Search

```bash
heliox document search "<query>"
```

Cross-document search is currently a placeholder and returns an explicit
not-implemented error. For now, read the target document and search the rendered
markdown locally.

## Safety

- Do not rewrite a whole document when a targeted edit works.
- Edits are anchored by exact text spans, never by position or line number.
- If a human may be editing concurrently, keep changes small and re-read after
  a contested edit.
