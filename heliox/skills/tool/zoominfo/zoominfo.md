# ZoomInfo (`heliox tool zoominfo -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. ZoomInfo is a
**flat provider** (not grouped): everything after `--` is the zoominfo tool's
own CLI. It is ZoomInfo's B2B sales-intelligence Enterprise API: find and
enrich people and companies.

```bash
heliox tool zoominfo [--account <key>] -- <group> <verb> [flags...]
```

## Connect (no OAuth, PKI credential)

ZoomInfo has no OAuth. The user connects by pasting three fields from the
**ZoomInfo Admin Portal**: `username`, `client_id`, and an RSA `private_key`
(PEM). Run `heliox tool zoominfo auth --json` and relay the link; the user
enters those three fields. The tool signs a JWT with the private key and
exchanges it for a short-lived access token on every call; you never handle
tokens. A ZoomInfo Enterprise API seat is required; there is no free tier.

## The mental model: Search then Enrich (read this first)

ZoomInfo's workflow is two stages, and they cost differently:

- **Search** (`contact search`, `company search`) finds candidate records by
  filters (title, company, domain, industry, location) and returns record
  **IDs** plus light hints. **Search consumes NO credit.** This is the default
  discovery step.
- **Enrich** (`contact enrich`, `company enrich`) pulls the full profile
  (email, phone, firmographics) for up to 25 IDs (or match keys). **Enrich
  CONSUMES A CREDIT per newly enriched record** (re-enriching the same record
  is free for 12 months). Treat enrich as an explicit, ID-driven action; don't
  enrich a whole search page speculatively.

Check remaining credits with `usage` before a large enrich. Use `lookup` to
discover valid request filters and `outputFields` instead of guessing.

## Commands

Search and enrich take the request body as JSON via `--body` (inline) or
`--file` (path, or `-` for stdin). Build the body from `lookup` results.

```bash
# Discover valid input filters / output fields (no credit)
heliox tool zoominfo -- lookup inputFields/contact --json
heliox tool zoominfo -- lookup outputFields/company --json

# Check remaining credits and request limits (no credit)
heliox tool zoominfo -- usage --json

# Find candidates: returns record IDs, no credit
heliox tool zoominfo -- contact search --body '{"jobTitle":"VP Marketing","companyName":"Acme"}' --json
heliox tool zoominfo -- company search --body '{"companyName":"Acme","industry":"Software"}' --json

# Enrich by the IDs from search: CONSUMES CREDITS
heliox tool zoominfo -- contact enrich --body '{"matchPersonInput":[{"personId":123}],"outputFields":["email","phone","jobTitle"]}' --json
heliox tool zoominfo -- company enrich --file ./company-enrich.json --json
```

The response is emitted as JSON verbatim; the enrich response reports the
credits it consumed; surface that to the user when cost matters.

## Footguns

- **Enrich spends money.** One credit per newly enriched record. Prefer
  `search` to scope, then enrich only the IDs you actually need. Check `usage`
  first for a big batch.
- **Enrich is capped at 25 records per call.** Batch larger sets across calls.
- **Field names evolve.** ZoomInfo is migrating its Legacy Enterprise API to a
  New API. If a filter or output field is rejected, run `lookup` to get the
  currently valid names rather than guessing.

## Error recovery

See [../SKILL.md](../SKILL.md). A `401 reconnect required` means the PKI
credential was rejected. Ask the user to reconnect via a fresh `auth` link.
