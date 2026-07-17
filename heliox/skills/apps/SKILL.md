---
name: apps
description: "Use `heliox app ...` to build and maintain a durable Helio App for a teammate — a hosted website or web application with workspace or public visibility, a private Helio-managed source repository, native Git, immutable built versions, request-driven Worker execution, per-App database (D1) and object storage (R2), viewer identity forwarding, hosted secrets, explicit deploys, history, rollback, delete, and restore. Trigger when a user asks to build, update, publish, deploy, add a database / login / API key to, change visibility, roll back, inspect, delete, or restore an App or website. A blessed starter template ships in `templates/starter/`. Git push never deploys."
user-invocable: false
metadata:
  requires:
    bins: ["heliox", "git"]
  cliHelp: "heliox app --help"
---

# Heliox Apps

Start by reading `../shared/SKILL.md`.

`heliox app` builds and hosts durable Apps for a teammate. Each App has a
private Helio-managed source repository, immutable version history, explicit
deployments, a stable hosted URL, workspace or public visibility, rollback, and
a bounded recovery window after delete. An App can be a static-facing site or a
request-driven application; both use the same Worker contract, and backend code
runs only when an HTTP request arrives. Apps can also declare capabilities — a
per-App database, object storage, the viewer's workspace identity, and hosted
secrets — so an App can hold real product state without a separate backend.

Use an App when the user wants a maintained website or web application with
source history and a stable hosted URL, including durable data, sign-in-aware
behavior, or outbound API calls. Use `heliox artifact` instead for an
org-private, self-contained HTML or markdown deliverable such as a one-off
report or dashboard. Apps and Artifacts have separate storage and lifecycle
contracts.

## Communicate clearly

Assume the requester is a nontechnical teammate who wants a working thing at a
URL, not a walkthrough of how it was built. Keep source control, credentials,
commits, branches, build steps, archives, versions, IDs, and deploy polling out
of user-facing messages. A typical arc is one short message when you start
building, and then the finished URL. When something blocks you, say what it
means for their App in plain language — not the command that failed.

- The deliverable is always the hosted URL and a sentence on what they can do
  with it. Never end with only a local build or "the code is ready."
- Say "your app," "the site," "a database," "sign-in," "an API key" — not
  "D1," "R2," "the Worker," "the ESM entrypoint," or "the manifest."
- Only surface a decision when it changes what you build. Don't ask the user to
  pick a framework, a package manager, or a storage engine.

## Choose the path

Pick the **fast path** only when all of these hold:

- it's a brand-new App with no existing source to preserve;
- one page or route satisfies the request;
- it needs no database, uploads, sign-in, hosted secrets, or multi-route
  structure; and
- the deliverable is a single private URL.

Use the **capability path** otherwise: any change to an existing App, any
multi-route App, and anything that needs durable data, file uploads, viewer
identity, or hosted secrets. When unsure which path fits, take the capability
path — it is a superset.

Either way, start from the bundled starter (below) rather than assembling a
Worker project by hand.

## Start from the starter template

A blessed starter ships in this skill at `templates/starter/`. It already
satisfies the build-output contract: a Worker entrypoint that serves static
assets and routes API requests, a valid `.helio/hosting.json`, and a zero-config
build. As the first step of a new App, copy it into the cloned source directory
**including its dotfiles** — the required manifest lives at `.helio/hosting.json`
and a glob like `templates/starter/*` silently omits it (and the `.gitignore`),
leaving an App that cannot deploy. Use a dotfile-preserving copy:

```bash
cp -R agents/plugins/heliox/skills/apps/templates/starter/. <clone-directory>/
```

Then shape the product on top of it. Its `README.md` documents the layout, the
build command, and where each capability plugs in.

Do not re-derive the Worker skeleton, the asset-serving fallback, or the hosting
manifest by hand, and do not introduce a second project shape. For an existing
App, preserve its structure, package manager, and `.helio/hosting.json`; do not
replace a working layout with the starter merely to use it.

## Shape the product

- Build the first screen around the requested product with concrete,
  product-specific copy and realistic content — not generic dashboard chrome or
  lorem placeholder.
- Keep the implementation tied to what was asked. Do not add speculative
  features, settings pages, or client state the product does not need.
- The starter's placeholder landing content is scaffolding: replace it
  completely, and update the App title and description to the real product
  before the final build.
- Run the starter's documented build in the runtime and fix real build
  failures before deploying. App Service accepts only prebuilt output; it never
  runs a package manager or build script for you.

## Add only requested capabilities

Each capability is one opt-in field in `.helio/hosting.json`, read by exactly
one part of the system. Absent field = capability absent. Add a capability only
when the requested product needs it; leave the rest out.

- **Database and object storage** — persistent records, accounts, uploads, or
  any state that must survive reloads. Read
  [`references/persistence-and-storage.md`](references/persistence-and-storage.md).
- **Viewer identity** — when the App should know who the signed-in workspace
  member is (personalized content, per-user records, attributing writes). Read
  [`references/identity.md`](references/identity.md).
- **Hosted secrets** — an API key or token the App's server code needs at
  runtime and that must never live in the source or the browser. Read
  [`references/secrets.md`](references/secrets.md).

Do not reach for browser `localStorage`/`sessionStorage` or in-memory state as
the source of truth for data the product is expected to remember; that is
device-local only. Do not embed a secret in a Worker module or in browser
JavaScript — public JavaScript cannot hold a secret.

## Offer design directions in chat

When the visual direction is open and the choice matters to the requester, post
two or three concrete option previews in the channel and ask which they prefer,
rather than describing options in words or building all of them. Render each
option as an image with `heliox tool image` (see the `image` skill) and attach
them to a single message. Keep this to one round; do not stall a simple request
behind a design poll.

## Add a social preview card (optional)

For a public-facing site where link unfurls matter, once the site's headline,
palette, and copy are stable, generate one landscape social card that reuses the
finished site's actual content and visual style, save it into the **source**
asset tree (for example `src/public/og.png`, so the build emits `dist/og.png`
and the managed repo keeps the asset for future rebuilds and rollbacks — never
save it only into the gitignored `dist/`), and wire Open Graph / X meta tags in
the page head using an absolute URL derived from the request host. Generate
exactly one card, inspect it for wrong or invented text, and omit the card
rather than shipping a generic fallback. Skip this for private/workspace Apps
and for plain internal tools where no one shares a link.

---

The rest of this skill is the mechanics spine: the exact commands and the
build-output contract. Follow `../shared/SKILL.md` for `--json` and identifier
conventions.

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
App and clone directory. After cloning, copy the starter into the clone with the
dotfile-preserving command in "Start from the starter template" (a `*` glob drops
the required `.helio/` manifest) before shaping the product.

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

## Build-output contract

Run the repository's documented production build in the runtime. The App's
project root must contain both of these canonical paths:

- `dist/server/index.js`: the Cloudflare Worker-compatible ESM entrypoint;
- `.helio/hosting.json`: Helio's private hosting manifest.

### The hosting manifest

`.helio/hosting.json` declares which capabilities the App uses. Every field is
optional; the minimal manifest is:

```json
{}
```

The accepted top-level fields are:

- `project_id` — an optional string, accepted for build-tool compatibility but
  ignored for provider identity; App Service owns that identity.
- `d1` — `null` (no database) or a logical binding name such as `"DB"`.
- `r2` — `null` (no object storage) or a logical binding name such as `"FILES"`.
- `identity` — `null` (no identity forwarding) or `"viewer"`.
- `env` — omitted or `[]` (no hosted secrets) or a list of secret names such as
  `["STRIPE_API_KEY"]`.

`d1`, `r2`, and every `env` name share one flat Worker env namespace, so they
must all be pairwise distinct and must not collide with the reserved `ASSETS`
binding. Unknown fields, duplicate fields, and out-of-grammar values fail
validation. The per-capability references cover how to declare and use each one.

### Layout

Regular `.js` files under `dist/server/**` are private Worker modules, and
`dist/.helio/**` is reserved private hosting metadata (including the
`dist/.helio/drizzle/**` database migration subtree). Only the remaining regular
files under `dist/**`, including `dist/client/**` when emitted, are static assets
whose paths relative to `dist/` are preserved. A static-facing App still needs
the Worker entrypoint; route those requests to the `env.ASSETS` binding. Do not
create a second flat-static bundle format.

The Worker handles incoming HTTP requests, reads its declared bindings and
hosted secrets from `env`, and can fetch external APIs. It is not an always-on
Node or Go server: do not design around a persistent process, daemon, cron job,
queue consumer, or long-running background task. WebSockets and other HTTP
upgrades are not available yet.

The project-root `.helio/hosting.json` is packaged privately as
`dist/.helio/hosting.json`; it is never a public asset. Raw Cloudflare Pages
`_worker.js`, `_worker.bundle`, `_routes.json`, and `functions/**` layouts are
unsupported. `.openai/hosting.json` is not accepted and must not be generated
or packaged.

The project root, `dist/`, `.helio/`, and hosting manifest must be real,
non-symlink paths. Heliox packages only `dist/**` plus `.helio/hosting.json`;
source files and repository metadata are excluded. The archive rejects unsafe
deployable paths, symlinks and special files, duplicate paths, oversized
content, and common secret-bearing paths by name. It does not scan JavaScript,
HTML, or other file contents for embedded credentials. Inspect the built
contents explicitly, and never place source credentials, `.env` files, private
keys, or hosted-secret values in the build output — hosted secrets are supplied
at deploy time, not committed (see [`references/secrets.md`](references/secrets.md)).

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

A deploy fails closed when a declared capability cannot be satisfied — a failed
database migration, or a declared secret name with no stored value. The prior
version keeps serving; the release never flips half-configured. When a deploy
reports a missing secret value, set the value and redeploy (see
[`references/secrets.md`](references/secrets.md)); do not retry blindly.

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
version, or call a provider-specific rollback API. A rollback redeploys the
target version's declared capabilities; a database migration in that version
runs against the live database, and its declared secrets must still be set.

## Delete and restore

Delete immediately blocks new mutations and removes every immutable release
owned by the App before it becomes recoverable. It retains the repository,
immutable versions, deployment history, current pointers, and the App's database
and object storage until the returned recovery deadline:

```bash
heliox app delete <app-id> --yes --json
```

`--yes` is required and delete is sensitive. A successful recoverable delete
means the canonical Helio App origin no longer serves the App. There is no
provider-generated origin or per-App route to verify; confirm both the App
status and the owned release inventory before reporting incident containment.
Preserve the returned `recoverable_until` value. Before that deadline, restore
republishes the retained current immutable version as a new release and
deployment attempt when one exists, and the retained database and object storage
carry their data forward:

```bash
heliox app restore <app-id> --json
```

After destructive cleanup begins, restore must fail rather than racing or
recreating partial resources; that final cleanup also purges the App's database,
object storage, and hosted secrets. Never describe a recoverable delete as
immediate permanent erasure.

## Recommended end-to-end path

1. `heliox app status APP --json` for an existing App, or `heliox app new ...
   --json` for a new one; copy the starter into a new clone with the
   dotfile-preserving `cp -R templates/starter/. <clone>/` (a `*` glob drops the
   required `.helio/` manifest).
2. Shape the product on the starter; add only the capabilities the request
   needs, declaring each in `.helio/hosting.json`.
3. Commit and `git push` with native Git.
4. Run the documented production build.
5. Inspect `dist/**` and `.helio/hosting.json` for the complete contract and
   accidental secrets.
6. For declared `env` secrets, ensure each value is set (see
   [`references/secrets.md`](references/secrets.md)) before deploying.
7. `heliox app deploy APP --dir PROJECT_ROOT --ref HEAD --json`.
8. Confirm the returned deployment, hosted URL, and App visibility with
   `status` and, when needed, `deployments`.
9. Report the exact hosted URL and what the user can do with it. Keep secrets,
   commits, and provider internals out of the report.

## Failure handling

- A create response followed by clone failure means the App exists. Recover
  with `app clone`; do not issue another `app new` blindly.
- An authentication failure from `git` is not a request for the user's GitHub
  token. Confirm the repository is the managed clone and its local credential
  helper is intact; then retry the Git operation once the App is active.
- A rejected archive is a local output-contract problem. Fix the build output;
  do not bypass validation or upload a different archive format.
- A deploy that fails with a missing-secret error needs the value set, then a
  redeploy — not a blind retry.
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
  build-time values; runtime secrets go through the hosted-secrets path.
- Forwarded viewer identity headers are server-authoritative and only trustworthy
  inside the Worker; never trust an identity value a browser sends. See
  [`references/identity.md`](references/identity.md).
- The App source credential belongs to Helio's GitHub App, not the user. User
  GitHub integrations are unrelated and must never be used as a fallback.
- App cleanup owns only App repositories, application-tagged release scripts,
  `apps/<app-id>/versions/*` archives, and the App's own database, object
  storage, and hosted secrets. It must never mutate the shared dispatcher or
  namespace, Artifact metadata, or Artifact Service `artifacts/*` objects.
