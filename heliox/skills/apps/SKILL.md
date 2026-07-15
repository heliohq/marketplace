---
name: apps
description: "Use `heliox app ...` to create and maintain a durable Helio App with workspace or public visibility, a private Helio-managed source repository, native Git, immutable built versions, request-driven Worker execution, explicit deploys, history, rollback, delete, and restore. Trigger when a user asks to build, update, publish, deploy, change visibility, roll back, inspect, delete, or restore an App. Git push never deploys."
user-invocable: false
metadata:
  requires:
    bins: ["heliox", "git"]
  cliHelp: "heliox app --help"
---

# Heliox Apps

Start by reading `../shared/SKILL.md`.

`heliox app` manages durable hosted Apps. Each App has a private Helio-managed
source repository, immutable version history, explicit deployments, a stable
hosted URL, workspace or public visibility, rollback, and a bounded recovery
window after delete. An App can be a static-facing site or a request-driven
application; both use the same Helio Sites Worker contract, and backend code
runs only when an HTTP request arrives.

Use an App when the user wants a maintained website or web application with
source history and a stable hosted URL, including request-driven backend logic
or outbound API fetches. Use `heliox artifact` instead for an org-private,
self-contained HTML or markdown deliverable such as a report or dashboard.
Apps and Artifacts have separate storage and lifecycle contracts.

## Non-negotiable behavior

- **A Git push never deploys.** Push source first, build locally, then run
  `heliox app deploy` as a separate, explicit action.
- Build source in the current runtime. App Service accepts only prebuilt output;
  it never runs package managers or project build scripts.
- Use native `git` commands in the cloned repository. Heliox installs a
  repository-local credential helper that mints a fresh, short-lived,
  repository-scoped credential when Git needs one.
- Never request, print, inspect, copy, persist, or place source credentials in a
  remote URL. Never invoke the hidden credential helper yourself. Do not
  replace it with a user's GitHub token or OAuth connection.
- Treat the source repository as Helio-managed and provider-opaque. Use the
  returned clone URL and native Git; never infer or expose an underlying GitHub
  repository URL.
- Prefer `--json` for every assistant-facing Heliox command.
- New Apps default to `workspace`: only people in the current Helio workspace
  can open them. A `public` App can be opened by anyone on the internet.
- Never widen an App to `public` without the user's explicit consent. Do not
  infer consent from a request to build, push, publish, or deploy. Pass `--yes`
  only after the user explicitly asks for public internet access.
- Delete, restore, rollback, deploy, and visibility changes affect hosted
  state. Perform them only when the user's request authorizes that outcome.

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

Clone an existing App only when it is active and you are authorized to edit it.
Gallery visibility alone does not grant source access. Source credentials are
available only while the App is active and not tombstoned. `APP` is the exact
24-hex App ID; the slug is display/routing metadata and is not a CLI identifier.
Retain the ID returned by create/list for subsequent commands.

## Inspect before changing

```bash
heliox app list --json
heliox app status <app-id> --json
```

Run `status` before editing an existing App. It shows the current lifecycle,
visibility, source, and deployment state without exposing provider identities
or credentials. If the command shape is uncertain, inspect live help instead
of guessing:

```bash
heliox app --help
heliox app deploy --help
```

## Visibility

Visibility belongs to the App, not to a deployment or hosting manifest.
Deploy, rollback, delete, and restore preserve the current choice.

Keep an App limited to the current Helio workspace:

```bash
heliox app visibility <app-id> workspace --json
```

Only after the user explicitly consents to world-readable access, make it
public and acknowledge that widening:

```bash
heliox app visibility <app-id> public --yes --json
```

`--yes` is deliberately required for `public` and must never be added merely
to get past the CLI gate. Narrowing back to `workspace` does not require it.
The Apps gallery displays visibility but does not offer an edit action because
workspace viewers are not necessarily App editors; use this editor-authorized
Heliox path instead.

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
package/build scripts. Do not assume a framework or build command; ensure the
result satisfies the canonical `dist/` contract below. Keep unrelated user
changes intact, stage only the intended files, and run the smallest relevant
checks before pushing.

After `git push`, the hosted App is still unchanged. Never tell the user a push
was deployed.

## Build the Helio Sites project

Run the repository's documented production build in the runtime. The App's
project root must contain both of these canonical files:

- `dist/server/index.js`: the Cloudflare Worker-compatible ESM entrypoint;
- `.helio/hosting.json`: Helio's private hosting manifest.

The canonical minimal hosting manifest is:

```json
{}
```

The only accepted top-level fields are an optional `project_id` string and
optional `d1` and `r2` fields whose values must be `null`. `project_id` is
accepted for Sites build-tool compatibility but ignored for provider identity;
App Service owns that identity. Unknown fields, duplicate fields, and non-null
bindings fail validation.

Regular `.js` files under `dist/server/**` are private Worker modules, and
`dist/.helio/**` is reserved private hosting metadata populated by Heliox from
the project-root manifest. Only the remaining regular files under `dist/**`,
including `dist/client/**` when emitted, are static assets whose paths relative
to `dist/` are preserved. A static-facing App still needs the Worker entrypoint;
route those requests to the `env.ASSETS` binding. Do not create a second
flat-static bundle format.

The Worker can handle incoming HTTP requests and fetch external APIs. It is not
an always-on Node or Go server: do not design around a persistent process,
daemon, cron job, queue consumer, or long-running background task. D1, R2,
runtime environment variables, hosted secrets, WebSockets, and other HTTP
upgrades are not available yet. Do not embed secrets in Worker modules or
browser JavaScript.

The project-root `.helio/hosting.json` is packaged privately as
`dist/.helio/hosting.json`; it is never a public asset. Raw Cloudflare Pages
`_worker.js`, `_worker.bundle`, `_routes.json`, and `functions/**` layouts are
unsupported. `.openai/hosting.json` is not accepted and must not be generated
or packaged.

The project root, `dist/`, `.helio/`, and hosting manifest must be real,
non-symlink paths. Heliox packages only `dist/**` plus
`.helio/hosting.json`; source files and repository metadata are excluded. The
archive rejects unsafe deployable paths, symlinks and special files, duplicate
paths, oversized content, and common secret-bearing paths by name. It does not
scan JavaScript, HTML, or other file contents for embedded credentials. Inspect
the built contents explicitly, and do not place source credentials, `.env`
files, private keys, or runtime-only secrets in the build output.

If the project needs always-on compute, scheduled ingestion, queues, persistent
storage, or secret-backed API credentials, stop: the current Apps runtime does
not provide those capabilities. Do not work around that boundary by embedding
secrets into Worker modules or browser JavaScript.

## Explicit deploy

After the source commit is pushed and the production build succeeds:

```bash
heliox app deploy <app-id> --dir <project-root> --ref HEAD --json
```

Deploy resolves `--ref` from the local clone, verifies that commit against the
managed remote repository, validates and stores an immutable built version,
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

Delete immediately blocks new mutations and removes every immutable release
owned by the App before it becomes recoverable. It retains the repository,
immutable versions, deployment history, and current pointers until the returned
recovery deadline:

```bash
heliox app delete <app-id> --yes --json
```

`--yes` is required and delete is sensitive. A successful recoverable delete
means the canonical Helio App origin no longer serves the App. There is no
provider-generated origin or per-App route to verify; confirm both the App
status and the owned release inventory before reporting incident containment.
Preserve the returned `recoverable_until` value. Before that deadline, restore
republishes the retained current immutable version as a new release and
deployment attempt when one exists:

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
5. Inspect `dist/**` and `.helio/hosting.json` for the complete contract and
   accidental secrets.
6. `heliox app deploy APP --dir PROJECT_ROOT --ref HEAD --json`.
7. Confirm the returned deployment, hosted URL, and App visibility with
   `status` and, when needed, `deployments`.
8. Report the exact hosted URL, visibility, App ID, source commit, version,
   deployment, and checks run. Keep secrets and provider internals out of the
   report.

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

- App source repositories are private. Workspace visibility gates the hosted
  origin to current workspace members; public visibility makes Worker responses
  world-readable. Remove confidential data and secrets before building either
  kind.
- A hosted URL does not imply public visibility. Read the App's `visibility`
  field before describing who can open it.
- The canonical App origin uses a registrable domain separate from Helio's
  trusted product and control-plane origins so broad `Domain` cookies and
  browser same-site semantics cannot cross into user Workers. Never construct,
  rewrite, or guess that hostname; use the returned `production_url` or
  `launch_url` exactly.
- Public JavaScript cannot safely hold a secret. Use only intentionally public
  build-time values.
- The App source credential belongs to Helio's GitHub App, not the user. User
  GitHub integrations are unrelated and must never be used as a fallback.
- App cleanup owns only App repositories, application-tagged release scripts,
  and `apps/<app-id>/versions/*` archives. It must never mutate the shared
  dispatcher or namespace, Artifact metadata, or Artifact Service `artifacts/*`
  objects.
