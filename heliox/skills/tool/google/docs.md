# Google Docs (`heliox tool google docs -- ...`)

Read [google.md](./google.md) for auth and account selection. Everything after
`--` is the docs tool's own CLI. Documents are addressed by **pasted link or
id**: every command that takes a document accepts a full
`https://docs.google.com/document/d/<id>/edit` URL or a bare id (the tool
extracts the id). There is no search: the Docs API has no list method, so when
the user wants "that doc", ask them to paste the link.

## Core commands

```bash
# Read (default renders markdown; --format text|json for alternatives)
heliox tool google docs -- documents get <doc|url>
heliox tool google docs -- documents get <doc|url> --format json          # raw structured API response
heliox tool google docs -- documents get <doc|url> --all-tabs             # multi-tab docs
heliox tool google docs -- documents get <doc|url> --suggestions inline   # show tracked suggestions

# Create / append (additive: never touches existing text)
heliox tool google docs -- documents create --title "Q3 Plan" --body-file ./plan.md
heliox tool google docs -- documents append <doc|url> --text "One more note."
heliox tool google docs -- documents append <doc|url> --body-file ./section.md

# Overwrite existing content (destructive: see the guardrail below)
heliox tool google docs -- documents replace-all <doc|url> --find "Q2" --replace "Q3"
heliox tool google docs -- documents batch-update <doc|url> --requests-file ./requests.json
```

You never compute document indices. Reads render the structured document to
markdown; `create`/`append --body-file` translate a markdown subset into the
API's edit requests for you. Check `-- --help` rather than guessing flags.

## Markdown you can write

`create --body-file` and `append --body-file` support: headings, paragraphs,
**bold**, *italic*, ~~strikethrough~~, `inline code`, `[text](url)` links, and
ordered / unordered lists. **Tables and images are not written**: the tool
warns and inserts them as literal text; for real tables/images use
`batch-update --requests-file` with raw Docs API requests. Reads *do* render
tables to markdown.

**List nesting flattens on write.** Indented sub-items in a `--body-file` are
written as a single-level list (all bullets/numbers at the top level): the
Docs API derives nesting from leading tabs it counts then strips, which is the
index-arithmetic danger zone the write subset deliberately avoids. Reads *do*
render nested lists with indentation. For a genuinely nested list, use
`batch-update --requests-file`.

## Guardrails: confirm before overwriting

Everything happens inside the user's own account (there is no "send to a third
party" action like email). The one risk tier that needs care is **overwriting
existing content**: `replace-all` and `batch-update`. At the API layer these
are not reversible (Docs version history can restore manually, but the tool
cannot). So:

- **Read before you overwrite.** Before any `replace-all` or `batch-update`,
  `get` the target document (or the target section) so the original text is in
  the conversation: that is your "before" snapshot.
- **`replace-all` always reports its count.** Relay the `occurrences` number to
  the user. "Replace Q2 with Q3" that quietly changes 40 places when they
  expected 1 is a nasty surprise: report the number.
- **Show a diff for big rewrites.** For a meaningful multi-paragraph overwrite,
  tell the user *what* will change and *to what*, get confirmation, then run it.
  Mention that Docs version history (File → Version history) can restore.

`create` and `append` only add content and are safe to run directly.
`batch-update` is treated as overwrite-tier regardless of its contents (the
tool does not parse the request JSON), so apply the read-before/confirm
discipline to every `batch-update`.

## Failure notes

- **404, or 403 "permission" without a scope hint** → the document is not
  shared with the connected account. This is the most common Docs failure: the
  user pasted a link shared with their account A while you are connected as
  account B. Ask them to share it with the connected account, or retry with
  `--account <other>`.
- **403 with a scope/reconnect hint** → the connection predates the `documents`
  scope; ask the user to disconnect and reconnect (fresh consent re-grants
  everything).
- **No connection** → `heliox tool google auth docs` to mint the authorize
  link, then relay it to the user.
- **`create --body-file` body write failed** → the document was still created
  (its URL is printed); the body just did not land. Tell the user, then
  `append` the content or retry.
- **400 on `batch-update`** → your `--requests-file` JSON is malformed or an
  index is out of range; the API error names the offending request. Fix the
  requests, do not blindly retry.
