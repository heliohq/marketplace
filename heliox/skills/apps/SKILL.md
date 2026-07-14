---
name: apps
description: "Use `heliox app ...` to create and maintain a durable public Helio App with a private Helio-managed source repository, native Git, immutable static versions, explicit deploys, history, rollback, delete, and restore. Trigger when a user asks to build, update, publish, deploy, roll back, inspect, delete, or restore an App. Git push never deploys."
user-invocable: false
metadata:
  requires:
    bins: ["heliox", "git"]
  cliHelp: "heliox app --help"
---

# Heliox Apps

Start by reading `../shared/SKILL.md`.

`heliox app` manages durable public, multi-file static Apps. Each App has a
private Helio-managed source repository, immutable version history, explicit
deployments, a stable public URL, rollback, and a bounded recovery window after
delete.

Use an App when the user wants a maintained website or frontend project with
source history and a public URL. Use `heliox artifact` instead for an
org-private, self-contained HTML or markdown deliverable such as a report or
dashboard. Apps and Artifacts have separate storage and lifecycle contracts.

## Non-negotiable behavior

- **A Git push never deploys.** Push source first, build locally, then run
  `heliox app deploy` as a separate, explicit action.
- Build source in the current runtime. App Service accepts only prebuilt static
  output; it never runs package managers, build scripts, or source code.
- Use native `git` commands in the cloned repository. Heliox installs a
  repository-local credential helper that mints a fresh, short-lived,
  repository-scoped credential when Git needs one.
- Never request, print, inspect, copy, persist, or place source credentials in a
  remote URL. Never invoke the hidden credential helper yourself. Do not
  replace it with a user's GitHub token or OAuth connection.
- Prefer `--json` for every assistant-facing Heliox command.
- Delete, restore, rollback, and deploy change public state. Perform them only
  when the user's request authorizes that outcome.

## Create and clone

Create a managed App and clone its private source repository:

```bash
heliox app new --title "<title>" --slug <slug> --directory <path> --json
heliox app new --title "<title>" --slug <slug> --owner @alice --directory <path> --json
```

`--owner` is an optional provisional human owner and must be an `@handle`.
Omit `--directory` to clone into the App slug. The JSON response includes the
App and clone directory.

If App creation succeeds but clone fails, the error names the created App ID.
Recover without creating a duplicate:

```bash
heliox app clone <app-id> <path> --json
```

Clone any existing active, visible App the same way. Source credentials are
available only while the App is active and not tombstoned. `APP` is the exact
24-hex App ID; the slug is display/routing metadata and is not a CLI
identifier. Retain the ID returned by create/list for subsequent commands.

## Inspect before changing

```bash
heliox app list --json
heliox app status <app-id> --json
```

Run `status` before editing an existing App. It shows the current lifecycle,
source, and deployment state without exposing provider identities or
credentials. If the command shape is uncertain, inspect live help instead of
guessing:

```bash
heliox app --help
heliox app deploy --help
```

## Edit and push source

Work inside the managed clone with ordinary development tools and native Git:

```bash
cd <clone-directory>
git status --short
# edit files and run the project's relevant checks
git add <paths>
git commit -m "<concise commit message>"
git push
```

Before building, read the repository's instructions and inspect its actual
package/build scripts. Do not assume a framework or output directory. Keep
unrelated user changes intact, stage only the intended files, and run the
smallest relevant checks before pushing.

After `git push`, the public App is still unchanged. Never tell the user a push
was deployed.

## Build and choose static output

Run the repository's documented production build in the runtime. Select the
resulting directory that contains the deployable static files (for example,
`dist/`, `build/`, or `out/` only when the project actually produces it).

The deploy directory must be a real, non-symlink directory containing only the
prebuilt static site. The archive rejects unsafe paths, symlinks and special
files, duplicate paths, oversized content, `_worker.js`, and `functions/`.
Do not include source credentials, `.env` files, private keys, server code, or
runtime-only secrets in the output.

If the project needs a server process, server-side secrets, Workers functions,
or dynamic execution, stop: the current Apps product is static hosting only.
Do not work around that boundary by embedding secrets into browser JavaScript.

## Explicit deploy

After the source commit is pushed and the production build succeeds:

```bash
heliox app deploy <app-id> --dir <output-directory> --ref HEAD --json
```

Deploy resolves `--ref` from the local clone, verifies that commit against the
managed remote repository, validates and stores an immutable static version,
then explicitly creates a deployment. Keep `--ref HEAD` unless the user asked
to deploy another local ref. A successful JSON response includes `version_id`,
`version_number`, `deployment_id`, `status`, and `production_url`.

Do not announce success from an ambiguous timeout. The command's bounded
automatic retries reuse its original idempotency keys, but a new
`heliox app deploy` invocation generates new keys and may create another version
or deployment. After an ambiguous exit, inspect `status`, version history, and
deployment history; do not blindly rerun deploy.

## Version and deployment history

```bash
heliox app versions <app-id> --limit 20 --json
heliox app deployments <app-id> --limit 20 --json
```

Each command returns one bounded newest-first page. If `next_cursor` is present,
request the next page explicitly:

```bash
heliox app versions <app-id> --limit 20 --cursor '<opaque-cursor>' --json
heliox app deployments <app-id> --limit 20 --cursor '<opaque-cursor>' --json
```

Treat cursors as opaque and resource-specific. Do not edit or reuse one across
Apps or between version and deployment history.

## Rollback

Rollback redeploys a previously successful immutable version as a new
deployment. It preserves all version and deployment history:

```bash
heliox app rollback <app-id> --version <version-id> --json
```

Choose the version from `heliox app versions` and verify the associated prior
deployment was successful. Rollback does not alter Git, rewrite an earlier
version, or call a provider-specific rollback API.

## Delete and restore

Delete immediately blocks new mutations, detaches the branded custom domain,
and deletes the deterministic hosting project before the App becomes
recoverable. It retains the repository, immutable versions, deployment history,
and current pointers until the returned recovery deadline:

```bash
heliox app delete <app-id> --yes --json
```

`--yes` is required and delete is sensitive. A successful recoverable delete
means neither the branded domain nor the provider-generated `pages.dev` URL
serves the App, but verify both authoritative reads before reporting incident
containment. Preserve the returned `recoverable_until` value. Before that
deadline, restore recreates the deterministic hosting project, republishes the
retained current immutable version as a new deployment attempt when one exists,
and reattaches the branded domain:

```bash
heliox app restore <app-id> --json
```

After destructive cleanup begins, restore must fail rather than racing or
recreating partial resources. Never describe a recoverable delete as immediate
permanent erasure.

## Recommended end-to-end path

1. `heliox app status APP --json` for an existing App, or `heliox app new ...
   --json` for a new one.
2. Edit and test the managed clone.
3. Commit and `git push` with native Git.
4. Run the documented production build.
5. Inspect the output directory for static-only content and accidental secrets.
6. `heliox app deploy APP --dir OUTPUT --ref HEAD --json`.
7. Confirm the returned deployment and public URL with `status` and, when
   needed, `deployments`.
8. Report the exact public URL, App ID, source commit, version, deployment, and
   checks run. Keep secrets and provider internals out of the report.

## Failure handling

- A create response followed by clone failure means the App exists. Recover
  with `app clone`; do not issue another `app new` blindly.
- An authentication failure from `git` is not a request for the user's GitHub
  token. Confirm the repository is the managed clone and its local credential
  helper is intact; then retry the Git operation once the App is active.
- A rejected archive is a local output-contract problem. Fix the build output;
  do not bypass validation or upload a different archive format.
- A permanent provider/auth/quota error needs operator attention. Do not repeat
  the same mutation unchanged.
- After any failed mutation, inspect `app status` and the relevant history
  before deciding whether to retry.
- Never narrate a push, version save, deployment, rollback, delete, or restore
  as successful unless the command or subsequent authoritative read proves it.

## Safety and privacy

- App source repositories are private, but deployed static bytes are public.
  Remove confidential data and secrets before building.
- Public JavaScript cannot safely hold a secret. Use only intentionally public
  build-time values.
- The App source credential belongs to Helio's GitHub App, not the user. User
  GitHub integrations are unrelated and must never be used as a fallback.
- App cleanup owns only App repositories, hosting projects/domains, and
  `apps/<app-id>/versions/*` archives. It must never mutate Artifact metadata or
  delete Artifact Service `artifacts/*` objects.
