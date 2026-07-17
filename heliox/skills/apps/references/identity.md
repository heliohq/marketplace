# Viewer identity

An App can receive the identity of the signed-in workspace member who opened it,
forwarded as request headers the Worker can trust. Read this when the product
needs to know who the current user is — personalized content, per-user records,
attributing writes, or a member-only surface.

## When to use it

Use viewer identity when the App legitimately needs the current member's
identity: a profile or account page, per-user saved data, "created by" on a
record, a dashboard scoped to the viewer, or a surface that should behave
differently for different members.

Do not declare it for a public landing page, static content, read-only shared
data, or device-local UI preferences. Identity forwarding covers **authenticated
workspace sessions only** — the member is already signed in to Helio and opened
the App from Helio. It is not a public sign-in system and does not let anonymous
internet visitors authenticate.

## Declaring it

Set the seat in the project-root `.helio/hosting.json`:

```json
{ "identity": "viewer" }
```

`"viewer"` is the only accepted value. With it declared, a workspace member who
opens a **workspace**-visibility App carries a launched session, and the
dispatcher stamps the viewer's identity onto every request that reaches the
Worker.

**Viewer identity only works for workspace-visibility Apps.** Under the current
dispatcher contract a `public` App authorizes anonymously and is never given
viewer headers — even when opened by a signed-in member with a launched session.
So do not build a personalized flow on viewer headers in a `public` App: it will
always behave anonymously. Keep the App at `workspace` visibility if it needs to
know who the viewer is.

## Reading the headers

Inside the Worker, read the stamped headers from the incoming request:

- `x-helio-user-id` — the member's stable user id (always present when a viewer
  is forwarded).
- `x-helio-org-id` — the member's workspace/org id (always present with a
  viewer).
- `x-helio-user-email` — the member's email (present when available).
- `x-helio-user-display-name` — the member's display name, **percent-encoded**.
  It is present only alongside
  `x-helio-user-display-name-encoding: percent-encoded-utf-8`; decode with
  `decodeURIComponent` only when that encoding header matches, and always fall
  back to email or id when the name is absent.

```js
const userId = request.headers.get("x-helio-user-id");
const orgId = request.headers.get("x-helio-org-id");
const email = request.headers.get("x-helio-user-email") ?? "";
let name = "";
if (
  request.headers.get("x-helio-user-display-name-encoding") ===
  "percent-encoded-utf-8"
) {
  name = decodeURIComponent(
    request.headers.get("x-helio-user-display-name") ?? "",
  );
}
```

Treat a request with no `x-helio-user-id` as anonymous and handle it explicitly
(render a public view, or reject a member-only route) rather than assuming a
viewer is always present.

## Trust boundary

The stamped headers are **server-authoritative**: the dispatcher strips every
inbound `x-helio-*` header from the incoming request before adding the validated
ones, so a value the Worker reads came from Helio, not from the browser. This
holds only inside the Worker.

- Never trust an `x-helio-*` value that arrives anywhere else, and never let
  browser JavaScript send one and expect it to be honored — it is stripped.
- Identity is authentication, not authorization. Knowing who the member is does
  not by itself decide what they may see. Keep access and ownership checks in
  server code: compare `x-helio-user-id` against a record's owner before
  returning or mutating it.
- A member-only route that depends on these headers must be dynamic per request
  (do not cache a response keyed to one viewer for another).

The starter in `../templates/starter/` includes a small helper that reads and
decodes these headers; use it rather than re-parsing headers in each route.
