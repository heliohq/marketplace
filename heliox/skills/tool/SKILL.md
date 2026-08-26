---
name: tool
description: "Connected tools portal: use `heliox tool ...` to see which external tools (Gmail, Slack, Notion, GitHub, Discord, LinkedIn, X, ...) are connected to you, ask the user to connect one (authorize link), and call a connected tool with credentials injected automatically. Covers the tool approval gate (`APPROVAL_REQUIRED` → `heliox approval request` → replay with `--approval`) and `heliox tool browser`: drive the user's paired local Chrome to browse the web. Trigger whenever a task needs an external service account (reading or sending the user's email, posting to Slack, editing Notion pages, working with GitHub repos), when a tool command exits with APPROVAL_REQUIRED, or when the user asks to connect/disconnect a tool."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox tool --help"
---

# Heliox Connected Tools

`heliox tool` is the portal to third-party accounts a human has connected to
you. Credentials never pass through your hands: the CLI fetches the right token
per call and injects it. Most providers are **flat**: one app, called as
`heliox tool <name>`; a few are **grouped** families called as
`heliox tool <provider> <app>` (see the model below). They all share one fixed
layout, so there is nothing to enumerate here: a provider's guide is
`./<name>/<name>.md`, `heliox tool <name> -- --help` is its full command
reference, and `heliox tool list --json` shows which accounts are connected.

One member is not an OAuth account: `heliox tool browser` drives the user's own
paired local Chrome for web-page work (open / click / fill / snapshot / eval).
It has its own connect + use model; see [browser/browser.md](./browser/browser.md).

## The model (learn once, applies to every provider)

1. **See what is connected**:

   ```bash
   heliox tool list --json
   ```

   Each row is one connected account on one provider. No row for a provider
   means nothing is connected; you cannot use it yet.

2. **Ask the user to connect** (you cannot authorize on their behalf):

   ```bash
   heliox tool <app> auth --json               # flat providers: slack, notion, x, ...
   heliox tool <provider> auth <app> --json    # grouped: google gmail; microsoft outlook / calendar / onedrive; zoho books / crm
   ```

   This mints a long-lived authorize link. Send that link to the user in the
   current conversation and explain in one line what you need the tool for.
   Whoever clicks it signs in and consents; you are woken with an
   `oauth_connected` event when the connection lands. Do not poll, and do not
   re-send the link unless it expired (you also get a `connect_intent_expired`
   wake) or the user asks again.

3. **Use the tool** (everything after `--` goes to the tool itself):

   ```bash
   heliox tool <app> [--account <key>] -- <tool args...>              # flat
   heliox tool <provider> <app> [--account <key>] -- <tool args...>   # grouped: google gmail; microsoft outlook; zoho books
   ```

   `--account` is only needed when the user connected more than one account of
   the same provider; a 409 error lists the candidate account keys to pick from.

4. **Acting as a person.** Some providers run either as you or as the human
   whose own account is connected (today: `lark`, via its own `-- ... --as
   user`). WHICH person is not yours to pick: Helio injects the identity of
   whoever asked in the batch that started this turn.

   **A question about someone's own data (their calendar, messages, files,
   mail) is a call as that person.** Run it as yourself and the provider
   answers about YOU: an empty result, `"ok": true`, no error, which reads
   exactly like "they have nothing". So before reporting such an answer, read
   the identity the response states (`"identity"` in the JSON; `-- whoami`
   asks outright). If it is not the person you were asked about, you did not
   read their data; say so instead of reporting what you got.

## Paginated reads

List and search commands may return only one page. Check the response for
pagination metadata and use the provider guide or `--help` for the matching
flag. Decide whether to continue based on the user's goal. If you stop while
more data exists, describe the result as partial.

## Approval gate

The highest-impact side-effect commands (sending email, social posts and DMs,
inviting new attendees, public shares and publishes) are policy-gated. Instead
of running, heliox exits with `APPROVAL_REQUIRED` on stderr plus the exact
next-step commands; that output is self-contained: follow it. The flow:

1. **Request**: `heliox approval request --message "<what, why, and the
   concrete content, in the approver's language>" -- tool <provider> ... --
   <cmd> ...`. The tail command after the first `--` is the same invocation
   that was intercepted, verbatim. Do **not** pre-confirm the action in chat
   first: the gate routes the decision to the right human (the person who
   authorized this account, who may not be whoever you are talking to); asking
   twice is double friction.
2. **Wait**: you are normally woken when the approval is decided. Still arm
   `schedule_wakeup` as a fallback right after requesting: the push can miss
   if this runtime is gone. Fallback prompt must cover every outcome: approved
   → replay with `--approval <id>`; denied → tell the user and stop; expired →
   re-request if the work is still needed (if it was approved but the window
   lapsed, say so in the new `--message`); cancelled → re-request only if
   still needed. If the fallback fires after the decision was already handled,
   do nothing and end the turn.
3. **Replay**: `heliox tool <provider> ... --approval <id> -- <same args>`
   (`--approval` goes before the first `--`, like `--account`). The approval
   binds the **literal** command: same tool, same `--account` form (omitted ⇔
   omitted, explicit ⇔ same value), same argv token-for-token; any change is
   an `APPROVAL_MISMATCH`. If the original command is no longer in context,
   recover it from `heliox approval get <id> --json` (the `extends` object
   carries `tool`, `account`, and `argv`) and replay verbatim.

Rules that keep the gate safe:

- **No-op guard, before any replay** (push wake or fallback): if the
  underlying command already ran (with or without an approval, under any id),
  do nothing and end the turn; if the command was superseded by a newer
  request, do not replay: tell the user the old card is abandoned (the new
  one is still pending) and end the turn. Judge by the command, not the
  approval id: the same command can have accumulated several ids.
- **Changing the argv or the approver means a new request** (there is no
  edit). Say in the new `--message` that it supersedes approval `<old-id>` and
  ask the approver to deny the old card; treat any later "approved" wake for
  the old id per the no-op guard above.
- **`APPROVAL_ALREADY_CONSUMED`: verify first, never resend blindly.** Check
  this turn's and prior tool output for whether the action actually executed;
  if you can't tell, use the provider's read-only commands or ask a human.
  Re-request only once you have confirmed it did not execute (the typical
  confirmed-failure case is `APPROVAL_CONSUMED_EXEC_FAILED`).
- **Multiple accounts on a provider: pass `--account` explicitly** when
  requesting. An approval requested without it binds to the omitted form, and
  the replay runs on whatever the primary connection is *then*; explicit
  `--account` pins the identity the approver actually approved.

## Error recovery

| Error | Meaning | What to do |
| --- | --- | --- |
| no connection / 4xx not connected | Provider not connected for you | Run the matching `auth` command and relay the link to the user |
| 409 with account candidates | Multiple accounts connected | Re-run with `--account <key>` from the candidate list |
| 401 reconnect required | Token revoked or expired for good | Ask the user to disconnect + reconnect via the auth link |
| 403 possibly missing scope | Connection predates a scope the command needs | Same: reconnect via a fresh auth link (consent re-prompts in full) |
| `APPROVAL_REQUIRED` on stderr | Command is policy-gated | Follow the printed steps (see "Approval gate" above) |
| `APPROVAL_*` on replay (denied / expired / pending / cancelled / mismatch / already consumed) | Approval credential not usable as-is | Follow the second stderr line; consumed → verify before any re-request ("Approval gate" above) |
| unknown tool in this heliox build | Version skew | Report it; the runtime needs a heliox upgrade. Do not improvise another path |

## Safety

- Outward-facing actions (email, posting under the user's name, inviting new
  people, public shares) go through the approval gate above **on service
  tools**: that card is the human check, not a chat confirmation.
- ⛔ **Binary tools run ungated.** `github` and `lark` reach the provider with
  nothing in between, so on those the outward-facing action happens the moment
  you run the command. Get the person's word for the actual content first; you
  are the only check there is.
- Ungated side effects still follow the per-family guidance (bulk-scale
  confirmation, destructive-edit confirmation in the `google/` and
  `microsoft/` docs) and the sensitive-operation rule: confirm before
  disconnect, revoke, or uninstall unless the user already asked.
- Never echo tokens or credential payloads; the CLI never shows them to you by
  design.

## Special cases

- `heliox tool browser ...` drives the user's paired local Chrome, not a
  connected account: its connect/use model differs from the OAuth flow above;
  see [browser/browser.md](./browser/browser.md).
- GitHub is org-installed (an admin installs the GitHub App once); if `auth`
  points you at an install/grant flow, relay those instructions instead.
