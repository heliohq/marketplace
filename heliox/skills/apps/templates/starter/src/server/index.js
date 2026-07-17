// Worker entrypoint for a Helio App.
//
// This is the only server file that must exist. It runs on every incoming HTTP
// request. Add API routes here, and let anything else fall through to the
// static assets built from `src/public/`.
//
// Capabilities are read from `env`, and are present only when declared in
// `.helio/hosting.json` (see the apps skill references):
//   - env.ASSETS            static assets (always present)
//   - env.DB                database, when `"d1": "DB"` is declared
//   - env.FILES             object storage, when `"r2": "FILES"` is declared
//   - env.<SECRET_NAME>     a hosted secret, when declared in `"env"`
//   - x-helio-user-* headers  the viewer, when `"identity": "viewer"` is declared

// readViewer returns the signed-in workspace member for this request, or null
// when no viewer identity is forwarded. The dispatcher strips any inbound
// x-helio-* headers and stamps validated ones, so these values are trustworthy
// only here inside the Worker — never trust an identity a browser sends.
function readViewer(request) {
  const userId = request.headers.get("x-helio-user-id");
  if (!userId) return null;
  let displayName = "";
  if (
    request.headers.get("x-helio-user-display-name-encoding") ===
    "percent-encoded-utf-8"
  ) {
    try {
      displayName = decodeURIComponent(
        request.headers.get("x-helio-user-display-name") ?? "",
      );
    } catch {
      displayName = "";
    }
  }
  return {
    userId,
    orgId: request.headers.get("x-helio-org-id") ?? "",
    email: request.headers.get("x-helio-user-email") ?? "",
    displayName,
  };
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Example API route. Replace with the product's real routes.
    if (url.pathname === "/api/hello") {
      const viewer = readViewer(request);
      return Response.json({
        ok: true,
        // `viewer` is null unless the App declares `"identity": "viewer"`.
        viewer: viewer && {
          userId: viewer.userId,
          displayName: viewer.displayName || viewer.email || viewer.userId,
        },
      });
    }

    // Everything else is served from the static build. Map the root to
    // index.html and hand the request to the assets binding.
    if (url.pathname === "/") url.pathname = "/index.html";
    return env.ASSETS.fetch(new Request(url, request));
  },
};
