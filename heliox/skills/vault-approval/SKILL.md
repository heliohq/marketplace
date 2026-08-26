---
name: vault-approval
description: "Use whenever credentials, API tokens, passwords, private keys, vault delegation, requestable credential search, approval polling, or owner/grantee credential flows require `heliox vault ...` or `heliox approval ...`."
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox vault --help"
---

# Heliox Vault And Approval

Use Helio vault for secret material. Use Helio approvals when a credential owner must decide whether to delegate a requestable credential. Vault discovery is org-scoped; plaintext access is still limited to owners and active delegates.

## Operating Rules

- Never print plaintext secrets in chat, logs, task comments, memory, wiki, or final summaries.
- Prefer metadata commands (`vault list`, `vault show`, `vault search`) before `vault get`.
- Use `vault get` only when plaintext is required for the immediate provider/tool call.
- Keep plaintext in the current process or shell for the shortest useful time.
- Use `request_ref` (`vcr_...`) for requestable credentials.
- Do not create duplicate requests while one is already pending for the same credential and purpose.
- Treat `delete`, `rotate`, `share`, and `unshare` as sensitive state-changing actions.

## Credential Shapes

Pass secret data as repeated `--data key=value` flags. Pass metadata as repeated `--metadata key=value` flags.

| Type | Required `--data` keys | Optional keys |
| --- | --- | --- |
| `password` | `username`, `password` | `email` |
| `token` | `access_token` | `refresh_token`, `id_token`, `token_type`, `expiry` |
| `keypair` | `private_key` | `public_key` |
| `multi_field` | at least one key/value | any useful key |

For token credentials, store the token value as `access_token`, not `token`.

## Credential Access Flow

Follow this order when a task needs a credential.

1. **Check credentials already available to the caller.**
   ```bash
   heliox vault list --role grantee --name <provider-or-purpose> --type token --json
   heliox vault list --role owner --name <provider-or-purpose> --type token --json
   heliox vault show <credential_id> --json
   ```
   Choose an active row whose name, type, owner, and safe metadata fit the current task. When several rows match, inspect metadata with `vault show`. Metadata filtering is not a `vault list` feature today.

2. **Search requestable previews when access is not already available.**
   ```bash
   heliox vault search --requestable <provider-or-purpose> --type token --json
   ```
   Search returns safe preview fields only: `request_ref`, `type`, `owner`, `display_name`, and `description`. It does not expose credential ids, private labels, metadata, timestamps, or plaintext.

3. **Request a matching credential by `request_ref`.**
   ```bash
   heliox vault request <request_ref> --policy trust --reason "<reason>" --json
   heliox vault request <request_ref> --policy trust --reason "<reason>" --wait 5m --json
   heliox vault request <request_ref> --policy onetime --reason "<reason>" --wait infinite --json
   heliox vault request <request_ref> --policy onetime --reason "<reason>" --expires "<rfc3339>" --json
   ```
   Without `--wait`, the command returns `status=pending` and an `approval_id`. With `--wait`, exit code `0` means approved; inspect JSON/status before continuing on any nonzero exit.

4. **Resolve the credential id after approval.**
   ```bash
   heliox approval get <approval_id> --json
   heliox vault list --role grantee --name <provider-or-purpose> --type token --json
   ```
   Use `credential.id` directly when an approved wait response includes it. Otherwise poll the approval or list delegated credentials after the owner approves.

5. **Fetch plaintext only for the immediate operation.**
   ```bash
   heliox vault get <credential_id> --json
   ```
   Redact the returned `data` object from user-visible output.

## Loading A Token For A Provider Tool

Map vault data to the env var expected by the provider tool. Confirm the native tool exists before relying on it.

```bash
credential_id=<credential_id>
export GITHUB_TOKEN="$(heliox vault get "$credential_id" --json | node -e 'let s="";process.stdin.on("data",c=>s+=c);process.stdin.on("end",()=>{const d=JSON.parse(s).data||{};if(!d.access_token)process.exit(1);process.stdout.write(d.access_token);})')"
export GH_TOKEN="$GITHUB_TOKEN"
command -v gh >/dev/null && gh auth status
```

Provider examples:

- GitHub CLI/API: `GITHUB_TOKEN` or `GH_TOKEN`.
- Slack API clients: usually `SLACK_TOKEN`.
- Other providers: use the provider's documented env/header name.

Never embed tokens in URLs unless the provider has no safer option. Prefer env vars, stdin, or documented auth headers.

## Storing Credentials

Store a credential when a token/account was created, secret material was rotated outside vault, or the user directly supplied secret material to preserve.

```bash
heliox vault store --name <private_label> --type token --data "access_token=<value>" --json
heliox vault store --name <private_label> --type password --data "username=<u>" --data "password=<p>" --json
heliox vault store --name <private_label> --type multi_field --data "api_key=<v>" --data "endpoint=<url>" --metadata "service=<provider>" --json
```

Treat `--name` as the private owner-side label. It is not the requestable search label. Add safe preview text only when future same-org agents should be able to discover and request this credential:

```bash
heliox vault store --name <private_label> --type token \
  --data "access_token=<value>" \
  --metadata "service=<provider>" \
  --metadata "username=<provider-username>" \
  --metadata "scopes=<scope-list>" \
  --requestable-name "<safe display name>" \
  --requestable-description "<safe usage description>" \
  --json
```

Share at creation when the grantee is already known:

```bash
heliox vault store --name <private_label> --type token \
  --data "access_token=<value>" \
  --share-with @<handle> \
  --policy trust \
  --share-reason "<reason>" \
  --json
```

## Updating, Rotating, And Deleting

Use `vault update` for metadata and the request preview (publish, rewrite, or unpublish). Use `vault rotate` to rewrite secret data.

```bash
heliox vault update <credential_id> --name <new_private_label> --json
heliox vault update <credential_id> --description "<safe description>" --metadata "service=<provider>" --json
heliox vault update <credential_id> --clear-expires --json
heliox vault update <credential_id> --requestable-name "<safe display name>" --requestable-description "<safe usage description>" --json
heliox vault update <credential_id> --clear-requestable --json
heliox vault rotate <credential_id> --data "access_token=<new_value>" --json
heliox vault delete <credential_id> --yes --json
```

When passing `--metadata`, include every metadata key that should remain. The metadata map is replaced when set.

- `--requestable-name` + `--requestable-description` must come **together**: they publish the credential to the request catalog, or rewrite the preview if it's already published (the existing request ref stays valid).
- `--clear-requestable` unpublishes it and can't be combined with the preview flags.
- An update passing none of these flags leaves the published state untouched.

## Sharing And Revoking

Share only credentials owned by the caller. Policies are `trust` or `onetime`.

```bash
heliox vault share <credential_id> --grantee @<handle> --policy trust --reason "<reason>" --json
heliox vault share <credential_id> --grantee @<handle> --policy onetime --expires "<rfc3339>" --reason "<reason>" --json
heliox vault shares <credential_id> --json
heliox vault outgoing-shares --json
heliox vault outgoing-shares --credential-id <credential_id> --json
heliox vault outgoing-shares --grantee @<handle> --json
heliox vault unshare <credential_id> <delegation_id> --reason "<reason>" --json
```

Use `vault shares <credential_id>` for delegations on one credential. Use `vault outgoing-shares` for delegations granted across credentials. Use `vault unshare` with both ids positionally.

## Approval Inspection

Inspect approvals when `vault request` returns pending, when a known approval id needs polling, or when the caller owns credentials and needs to review incoming requests.

```bash
heliox approval list --role asker --status pending --limit 20 --json
heliox approval list --role approver --status pending --limit 20 --json
heliox approval list --role approver --cursor <opaque> --json
heliox approval get <approval_id> --json
```

`--role` is required: `asker` or `approver`. Filters are `--status pending|decided`, `--limit`, and `--cursor`. Owner-side decisions happen through the desktop approval card today; the CLI surface creates domain requests and inspects/polls approvals.

Approvals also carry **tool-execution** requests (the tool approval gate):

- A policy-gated `heliox tool` command exits `APPROVAL_REQUIRED`; you create the request with `heliox approval request`, then replay the identical command with `--approval <id>` once approved.
- `approval get <id>` reports a derived `Status` (pending / approved / denied / cancelled / expired / consumed; approved credentials expire when the execution window lapses).
- `--json` exposes the frozen command under the top-level `extends` object (`tool`, `account`, `argv`): recover the exact command to replay when it has fallen out of context.

Full gate flow: the `heliox:tool` skill.

Wait outcome codes for `vault request --wait`:

| Code | Meaning |
| --- | --- |
| 0 | approved |
| 1 | denied |
| 2 | expired or wait-flag parse error |
| 3 | cancelled |
| 4 | unknown terminal outcome |
| 124 | wait duration exhausted while approval remains pending |
| 130 | interrupted while waiting |

## External-Service Credential Ladder

For GitHub, Slack, Linear, OpenAI, and similar providers, first name the
provider, credential type, needed scope, and risk level, then run the
**Credential Access Flow** above (owned/delegated → search requestable →
request → resolve → get plaintext). Beyond that Flow:

- **Nothing available or requestable** → create a new provider account/token,
  store it as `type=token` with `access_token=<value>`, and publish safe
  requestable preview text only when future agents should discover it.
- **Signup blocks** (CAPTCHA, a missing invite permission, verification
  trouble, an unclear provider form) → ask a human in DM/channel.
- **Acting with the credential** → outward-facing actions on connected tools
  are gated automatically by `heliox tool` (`APPROVAL_REQUIRED`; see
  `heliox:tool`); for destructive provider actions outside that gate (e.g.
  raw-credential calls), ask a human first.

Routine reads, clone, branch push, PR creation, issue comments, and
non-destructive API calls usually do not need a separate approval after
credential access is granted. Destructive or authority-changing actions do:
repo deletion, org settings, admin-scope token creation, force-pushing
protected branches, billing changes, access grants, and secret rotation.
