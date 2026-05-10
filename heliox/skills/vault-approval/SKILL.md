---
name: vault-approval
description: "Use `heliox vault ...` and `heliox approval ...` for credentials, API tokens, passwords, secret delegation, approval polling, and owner/grantee flows. Trigger whenever the assistant needs to store, fetch, rotate, request, share, revoke, or inspect credentials, or when an approval id/status appears."
user-invocable: false
metadata:
  requires:
    bins: ["heliox"]
  cliHelp: "heliox vault --help"
---

# Heliox Vault And Approval

Start by reading `../shared/SKILL.md`.

The vault holds secrets. You own credentials you create and can use credentials delegated to you.

## Safety

- Never print plaintext secrets in chat or logs.
- Prefer `vault show` for metadata. Use `vault get` only when plaintext is required for the immediate operation.
- Store structured data as JSON or `@file`.
- Treat `delete`, `rotate`, `share`, and `unshare` as sensitive.

## Own and delegated credentials

```bash
heliox vault list --json
heliox vault list --source delegated --json
heliox vault list --name <substring> --type password|token|keypair|multi_field --json
heliox vault list --include-invalid --json
heliox vault show <credential_id> --json
heliox vault get <credential_id> --json
```

`vault get` returns plaintext. Redact it from user-visible summaries.

## Store and update

```bash
heliox vault store --name <label> --type token --data '{"access_token":"..."}' --json
heliox vault store --name <label> --type multi_field --data @secret.json --description "<text>" --metadata '{"service":"github"}' --expires-at "<iso8601>" --json
heliox vault update <credential_id> --name <new_label> --json
heliox vault update <credential_id> --description "<text>" --metadata '{"key":"value"}' --expires-at "<iso8601>" --json
heliox vault update <credential_id> --clear-expires-at --json
heliox vault rotate <credential_id> --data '{"access_token":"new"}' --json
heliox vault delete <credential_id> --json
```

`vault update` changes metadata only. `vault rotate` merges a partial payload into credential data.

## Request someone else's credential

```bash
heliox vault request --owner <user_id> --name <label> --policy trust|always|onetime --reason "<why>" --json
heliox vault request --owner <user_id> --name <label> --policy trust|always|onetime --wait 5m --json
heliox vault request --owner <user_id> --name <label> --policy trust|always|onetime --wait infinite --json
```

Optional delegation expiry:

```bash
heliox vault request --owner <user_id> --name <label> --policy onetime --expires "<rfc3339>" --json
```

No `--wait`: returns `status=pending` and an `approval_id`. Do not create duplicate requests for the same credential while one is pending.

Exit codes for wait:

| Code | Meaning |
| --- | --- |
| 0 | approved |
| 1 | denied |
| 2 | expired |
| 3 | cancelled |
| 124 | wait timed out |
| 130 | interrupted |

After approval, list delegated credentials and fetch the needed credential:

```bash
heliox vault list --source delegated --json
heliox vault get <credential_id> --json
```

## Share and revoke credentials you own

```bash
heliox vault share <credential_id> --with <user_id> --policy trust|always|onetime --reason "<why>" --json
heliox vault share <credential_id> --with <user_id> --policy onetime --expires "<rfc3339>" --json
heliox vault shares --json
heliox vault shares <credential_id> --json
heliox vault shares --credential-id <credential_id> --json
heliox vault shares --grantee <user_id> --json
heliox vault unshare <credential_id> --delegation <delegation_id> --reason "<why>" --json
```

## Approval inspection

```bash
heliox approval list --role asker --json
heliox approval list --role approver --status pending --limit 20 --json
heliox approval get <approval_id> --json
```

Use `approval get` when a domain command tells you to poll an approval later.
