---
name: tool
description: "Connected third-party tools portal: use `heliox tool ...` to see which external tools (Gmail, Slack, Notion, GitHub, Discord, LinkedIn, X, ...) are connected to you, ask the user to connect one (authorize link), and call a connected tool with credentials injected automatically. Trigger whenever a task needs an external service account — reading or sending the user's email, posting to Slack, editing Notion pages, working with GitHub repos — or when the user asks to connect/disconnect a tool. Not for generic web browsing (that is the separate `browser` skill)."
user-invocable: false
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox tool --help"
---

# Heliox Connected Tools

Start by reading `../shared/SKILL.md`.

`heliox tool` is the portal to third-party accounts a human has connected to
you. Credentials never pass through your hands: the CLI fetches the right
token per call and injects it into the tool. Some providers are **grouped** by
family, each app connected and called on its own:

- Google (Gmail today) under `heliox tool google` — see
  [google/google.md](./google/google.md) for the family auth model and
  [google/gmail.md](./google/gmail.md) for the gmail command surface.
- Microsoft (Outlook / Calendar / OneDrive) under `heliox tool microsoft` —
  see [microsoft/microsoft.md](./microsoft/microsoft.md) for the family and
  [microsoft/outlook.md](./microsoft/outlook.md),
  [microsoft/calendar.md](./microsoft/calendar.md),
  [microsoft/onedrive.md](./microsoft/onedrive.md) for each app.

## The model (learn once, applies to every provider)

1. **See what is connected**:

   ```bash
   heliox tool list --json
   ```

   Each row is one connected account on one provider. No row for a provider
   means nothing is connected — you cannot use it yet.

2. **Ask the user to connect** (you cannot authorize on their behalf):

   ```bash
   heliox tool <app> auth --json               # flat providers: slack, notion, x, ...
   heliox tool <provider> auth <app> --json    # grouped: google gmail; microsoft outlook / calendar / onedrive
   ```

   This mints a long-lived authorize link. Send that link to the user in the
   current conversation and explain in one line what you need the tool for.
   Whoever clicks it signs in and consents; you are woken with an
   `oauth_connected` event when the connection lands — do not poll, and do not
   re-send the link unless it expired (you also get a `connect_intent_expired`
   wake) or the user asks again.

3. **Use the tool** — everything after `--` goes to the tool itself:

   ```bash
   heliox tool <app> [--account <key>] -- <tool args...>              # flat
   heliox tool <provider> <app> [--account <key>] -- <tool args...>   # grouped: google gmail; microsoft outlook
   ```

   `--account` is only needed when the user connected more than one account of
   the same provider; a 409 error lists the candidate account keys to pick from.

## Error recovery

| Error | Meaning | What to do |
| --- | --- | --- |
| no connection / 4xx not connected | Provider not connected for you | Run the matching `auth` command and relay the link to the user |
| 409 with account candidates | Multiple accounts connected | Re-run with `--account <key>` from the candidate list |
| 401 reconnect required | Token revoked or expired for good | Ask the user to disconnect + reconnect via the auth link |
| 403 possibly missing scope | Connection predates a scope the command needs | Same: reconnect via a fresh auth link (consent re-prompts in full) |
| unknown tool in this heliox build | Version skew | Report it; the runtime needs a heliox upgrade — do not improvise another path |

## Safety

- Anything that leaves the user's account (sending email, posting messages,
  creating public content) is an outward-facing action: follow the sensitive-
  operation rule from `../shared/SKILL.md` and the per-family guidance (for
  Gmail and Outlook, prefer the drafts flow in
  [google/gmail.md](./google/gmail.md) /
  [microsoft/outlook.md](./microsoft/outlook.md); for Calendar and OneDrive,
  confirm before notifying attendees or creating share links).
- Never echo tokens or credential payloads; the CLI never shows them to you by
  design.

## Special cases

- `heliox tool browser ...` is a cloud Chrome session, not a connected
  account — it has its own skill (`../browser/SKILL.md`).
- GitHub is org-installed (an admin installs the GitHub App once); if `auth`
  points you at an install/grant flow, relay those instructions instead.
