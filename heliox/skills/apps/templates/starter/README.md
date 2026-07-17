# Helio App starter

A minimal, zero-dependency Helio App: one Worker that serves static pages and
API routes. Copy this into a cloned App source directory and build the product
on top of it. It satisfies the Helio App build-output contract out of the box.

## Layout

```
.helio/hosting.json   capability declarations (starts empty: {})
src/public/           static assets — index.html and anything served to browsers
src/server/index.js   the Worker entrypoint (runs on every request)
build.mjs             assembles dist/ from src/  (no dependencies)
package.json          `npm run build` → node build.mjs
```

## Build

```bash
npm run build
```

This writes the deploy output:

```
dist/index.html       (and the rest of src/public/**)
dist/server/index.js  (and any other src/server/**.js modules)
```

There is nothing to install — the build is a plain file assembly. Then deploy
with `heliox app deploy <app-id> --dir . --ref HEAD --json` (push the source
first; a push never deploys).

## Adding capabilities

Each capability is one field in `.helio/hosting.json`. Add only what the product
needs; leave the rest out. See the apps skill references for the full guides.

### Database (D1) and object storage (R2)

Declare the bindings, then read them from `env`:

```json
{ "d1": "DB", "r2": "FILES" }
```

```js
await env.DB.prepare("SELECT * FROM notes WHERE id = ?").bind(id).all();
await env.FILES.put(key, body);
```

Ship schema as SQL migrations written to `dist/.helio/drizzle/` in the build
(applied before the release flips; a failing migration fails the deploy). Add a
step to `build.mjs` that writes your `.sql` files there, for example:

```js
await mkdir(resolve(dist, ".helio/drizzle"), { recursive: true });
await cp(resolve(root, "migrations"), resolve(dist, ".helio/drizzle"), {
  recursive: true,
});
```

Separate multiple statements in one `.sql` file with a `--> statement-breakpoint`
line. See `references/persistence-and-storage.md`.

### Viewer identity

```json
{ "identity": "viewer" }
```

The Worker's `readViewer(request)` helper (in `src/server/index.js`) returns the
signed-in workspace member, or `null` when no viewer is forwarded. These headers
are trustworthy only inside the Worker. See `references/identity.md`.

### Hosted secrets

Declare the names, set the values out of band, and read them from `env`:

```json
{ "env": ["STRIPE_API_KEY"] }
```

```bash
printf %s "$STRIPE_KEY" | heliox app env set <app-id> STRIPE_API_KEY --json
```

```js
const key = env.STRIPE_API_KEY; // server-side only; never return it to a client
```

Setting a value takes effect on the next deploy; a declared name with no stored
value fails the deploy closed. See `references/secrets.md`.

## Before deploying

Replace the placeholder title, description, and landing content with the real
product. Every binding name across `d1`, `r2`, and `env` must be distinct and
must not be `ASSETS`. Never commit secret values, `.env` files, or private keys.
