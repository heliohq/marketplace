# Hosted secrets

An App can declare named secrets whose values are stored in the Helio vault and
injected into the Worker's `env` at deploy time. Read this when the App's server
code needs an API key, token, or other credential at runtime that must never
appear in the source repository or the browser.

## When to use it

Use a hosted secret for a runtime credential the Worker uses server-side: a
third-party API key (payments, email, maps), a signing secret, an outbound
service token. The value is injected into `env.<NAME>` inside the Worker, so it
never appears in the repository, the browser, or `env list`.

**A hosted secret is only as safe as the Worker code it lands in.** The value
arrives as plaintext in `env`; any code in the Worker can log it, forward it in
an outbound request, or return it in a response. Helio keeps it out of the
repo and the browser, but it cannot stop the App's own server code from leaking
it. So before you store a real credential:

- **Own and read the server code that will use it.** Confirm the Worker reads
  the secret only where it's needed and never logs it, echoes it, or returns it
  to the client.
- **Confirm with the requester before `app env set`** whenever you're putting a
  real credential into an existing App, code you did not write, or a `public`
  App — say plainly that the value goes into the running server code, and get
  explicit go-ahead. Never inject a user's credential into untrusted or
  unreviewed App code on your own initiative.
- Prefer a **narrowly-scoped or test key** when one is available.

Do not use a hosted secret for an intentionally public, build-time value (a
public API base URL, a publishable client key) — bake those into the build. Do
not put a real secret in a Worker module, in browser JavaScript, in the
repository, or in the build output; public JavaScript cannot hold a secret.

## The two halves: declare the name, then set the value

A secret has a **name** (in the manifest, committed) and a **value** (in the
vault, never committed). They are managed separately.

1. **Declare the names** in the project-root `.helio/hosting.json` `env` list:

   ```json
   { "env": ["STRIPE_API_KEY"] }
   ```

   Each name must be a valid binding identifier, distinct from the `d1`/`r2`
   names and from the reserved `ASSETS` binding. Names only — the manifest never
   holds values.

2. **Set the values** with `heliox app env`. The value is read from a file or
   stdin, never from a command argument, so it can't leak through shell history
   or a process listing:

   ```bash
   printf %s "$STRIPE_KEY" | heliox app env set <app-id> STRIPE_API_KEY --json
   heliox app env set <app-id> STRIPE_API_KEY --value-file /path/to/key --json
   ```

## Deploy-time semantics

Setting or removing a value takes effect on the **next deploy** — the currently
published release keeps whatever it was deployed with. A deploy fails closed if
the serving version declares a secret name that has no stored value: the release
never flips half-configured, and the prior version keeps serving. So the order
for a new secret is: declare the name in the manifest, set the value, then
deploy.

If a deploy reports a missing secret value, set the value and redeploy — do not
retry the deploy blindly.

## Inspecting and removing

`list` shows each declared name and its state — whether a value is stored for
the next deploy (`set`) and whether the serving version declares it (`live`) —
and **never** prints a value:

```bash
heliox app env list <app-id> --json
```

`unset` removes a stored value; it too takes effect on the next deploy. If the
serving version still declares the name, the running App keeps its deployed
value until the next deploy, and that next deploy will fail closed until the
name is either set again or removed from the manifest:

```bash
heliox app env unset <app-id> STRIPE_API_KEY --json
```

## Reading a secret in the Worker

Declared secrets arrive as members of the Worker `env`, alongside the storage
and identity bindings:

```js
export default {
  async fetch(request, env) {
    const key = env.STRIPE_API_KEY; // present when declared and set
    // use key server-side only; never return it to the client
  },
};
```

Never echo a secret value back to the client, log it, or embed it in a response
body or a static asset. The value exists only inside the Worker at request time.

## Lifecycle and privacy

Hosted secret values live in the vault, are injected only at deploy time, and
are never written to the source, the build archive, or any list output. They are
retained through a recoverable delete and purged by final destructive cleanup
after the recovery deadline. Never surface a secret's value to the requester; if
they need to rotate one, have them provide the new value into `env set`.
