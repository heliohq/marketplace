# Hotjar (`heliox tool hotjar`)

Hotjar (now part of Contentsquare) captures product-experience data: surveys,
feedback, heatmaps, recordings. This tool wraps its REST API's read surface:
enumerate a site's surveys and export their responses (voice-of-customer
feedback), plus a GDPR/ops user lookup. Use it when a task needs survey feedback
for a site or needs to find what data Hotjar holds on a person.

Read `../SKILL.md` first for the connect/use model. Hotjar is a **flat**
provider (`heliox tool hotjar -- …`).

## Connect

Hotjar uses the user's own API credentials, not an OAuth consent screen. When
`heliox tool list` shows no hotjar row, ask the user to connect:

```bash
heliox tool hotjar auth --json
```

Relay the link. In the connect drawer the user pastes two values minted by an
**Admin** at **Hotjar → Settings → API**: the **client ID** and the **client
secret**. Two plan-tier facts to relay up front:

- **Survey responses export requires the Ask Scale plan.** User lookup requires
  at least Observe Scale. On a lower plan the API returns `403` and the tool
  reports a credential/permission error.
- **API keys auto-expire after one year and cannot be extended.** When a
  previously-working connection starts returning credential-rejected errors, the
  key has likely expired. Ask the user to mint a new one and reconnect.

The tool exchanges the pasted client_id/client_secret for a short-lived bearer
itself (OAuth client-credentials); you never handle a token.

## Commands

Everything after `--` goes to the tool. Every command emits JSON. Site,
survey, and organization IDs come from Hotjar's **Sites & Organizations** page.

```bash
# List a site's surveys (cursor-paginated). Pick a survey_id for responses.
heliox tool hotjar -- survey list --site 12345

# One survey's detail; add --with-questions for its question metadata.
heliox tool hotjar -- survey get --site 12345 --survey 678

# Export a survey's responses, newest first (cursor-paginated). Primary read.
heliox tool hotjar -- survey responses --site 12345 --survey 678

# GDPR/ops: find what Hotjar captured for a data subject, by email.
heliox tool hotjar -- user lookup --org 99 --email jane@example.com
```

### Pagination

`survey list` and `survey responses` return `{ "results": [...], "next_cursor":
"..." }`. When `next_cursor` is non-null, pass it back with `--cursor` to get the
next page; a null `next_cursor` means there are no more results. `--limit`
caps the page size.

```bash
heliox tool hotjar -- survey responses --site 12345 --survey 678 --cursor eyJ... --limit 100
```

## Cost & safety

- All commands are **read-only**. There is deliberately **no delete command**:
  Hotjar's user-lookup endpoint doubles as its data-deletion endpoint (via a
  `delete_all_hits` flag), so `user lookup` always sends the read-only mode and
  cannot delete. If a user genuinely needs a GDPR deletion, direct them to
  Hotjar's own UI. This tool will not perform it.
- A `403` means the key lacks permission or the account's plan tier does not
  include the feature (survey export needs Ask Scale). A credential-rejected
  error means the key is wrong or has hit its one-year expiry. Ask the user to
  reconnect with a fresh key.
- A `429` is Hotjar's rate limit (3000 requests/minute); retry after a short
  pause rather than reconnecting.
- Survey responses and user-lookup results are personal information: use them
  only for the task the user asked for; do not bulk-export or repurpose them.
