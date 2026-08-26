# Supabase (`heliox tool supabase -- ...`)

Read [../SKILL.md](../SKILL.md) first for the connect/use model. This provider
wraps the pinned official Supabase CLI. Management operations and linked
database queries use the connected user's OAuth access token; local database
queries use the official CLI's own target behavior.

```bash
heliox tool supabase [--account <key>] -- <group> <verb> [flags...]
```

The provider does not expose Supabase login/logout, local stack lifecycle,
migrations, arbitrary command paths, or Edge Function deployment. Database
execution is limited to `db query`; starting or stopping a local stack remains
outside the command surface. The connected OAuth grant is read-only for
Storage, so uploads and deletions are not supported. For an allowed command
path, arguments and flags are passed unchanged to the official CLI, which
remains the source of truth for their validation and behavior. Run `heliox tool
supabase -- --help` for the registered command tree and the official CLI help
for current flags.

## Find the organization and project first

Most management operations require an explicit 20-character project ref.
Resolve it from the connected OAuth grant rather than guessing:

```bash
heliox tool supabase -- orgs list
heliox tool supabase -- projects list
```

The token acts on behalf of the Supabase user who approved the connection. The
organizations, projects, and actions it can reach are still limited by that
user's Supabase membership and the permissions configured on Helio's OAuth app.

## Query a database

`db query` preserves the official CLI's linked/local target selection and
inline SQL input. The wrapper does not parse SQL, add `--linked`, or choose a
project:

```bash
# Query a remote project through the connected Supabase integration
heliox tool supabase -- db query "select id from public.accounts" --linked --project-ref <ref>

# Query an already-running local Supabase database
heliox tool supabase -- db query "select 1" --local --workdir <dir>
```

For remote databases, always use the integration path above. Do not ask for a
database password or construct a connection string. The official CLI uses the
connected OAuth identity and project ref to obtain the temporary database login
it needs. If Supabase rejects that flow, report the CLI error instead of
switching to password-based authentication.

If no target flag is supplied, the official CLI defaults to its local target.
`--local` does not use the OAuth token to authenticate to Postgres; the target
database must already be reachable from the active runtime.

## Common remote operations

```bash
# Inspect deployed resources and configuration
heliox tool supabase -- functions list --project-ref <ref>
heliox tool supabase -- branches list --project-ref <ref>
heliox tool supabase -- backups list --project-ref <ref>
heliox tool supabase -- secrets list --project-ref <ref>
heliox tool supabase -- storage ls ss:///bucket/prefix --project-ref <ref>

# Generate schema types through the Management API, not a local database
heliox tool supabase -- gen types --project-id <ref> --lang typescript

# Download remote artifacts to the current runtime filesystem
heliox tool supabase -- functions download my-function --project-ref <ref> --workdir <dir>
heliox tool supabase -- storage cp ss:///bucket/path ./destination --project-ref <ref>
```

Other read surfaces cover custom/vanity domains, network bans and restrictions,
Postgres configuration overrides, SQL snippet downloads, SSL enforcement, and
SAML SSO metadata. Check the leaf help before constructing flags:

```bash
heliox tool supabase -- network-restrictions update --help
```

## Official CLI gates and bundling

The wrapper leaves Supabase's experimental and confirmation gates under caller
control instead of enabling them automatically:

- If the official CLI reports `must set the --experimental flag`, retry the
  same operation with `--experimental`. This is required by experimental
  command groups such as Storage; it does not bypass Helio approval.
- The wrapped process has no interactive stdin. If a Supabase confirmation
  prompt falls back to its default and returns `context canceled`, retry with
  `--yes` only when the requested operation is clear and Helio approval covers
  it. Approval binds the literal argv, so adding `--yes` requires a new
  approval request. Do not add `--yes` to read commands.
- Function download preserves the official CLI's Docker/API selection. Add
  `--use-api` only when server-side unbundling is required or Docker should not
  be used. The deployment restriction below still applies to `functions
  deploy`.

## Safety

- Every `db query` invocation goes through the approval gate, including a
  query that appears read-only. Follow the `APPROVAL_REQUIRED` instructions;
  do not bypass the gate by choosing a different target or input form.
- Every `storage cp` invocation also goes through approval. Use an `ss://`
  source and a local destination; the connected OAuth grant does not permit
  uploads.
- Pass SQL inline. Helio does not accept `--db-url` because it directly targets
  an arbitrary PostgreSQL database outside the connected Supabase project, or
  `--file` because approval cannot bind the file contents. Use `--linked
  --project-ref <ref>` or an already-running local database instead.
- Helio does not currently accept `functions deploy` because approval binds the
  command but cannot prove that source files in the workdir stayed unchanged.
  Use an operator-controlled deployment workflow until source-bound approval is
  available.
- Confirm before any command that creates, updates, deploys, pauses, unpauses,
  removes, or deletes remote state. In particular, never run `projects delete`,
  `branches delete`, or `functions delete` from an ambiguous request.
- Project API-key retrieval is outside the command surface. `secrets list`
  returns metadata, not secret values.
- Local outputs from `functions download`, `storage cp`, `snippets
  download`, and `gen types` belong to the active runtime filesystem. Use an
  explicit destination/workdir and avoid overwriting unrelated files.
