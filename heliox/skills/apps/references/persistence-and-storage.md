# Persistence and storage

An App can declare a per-App SQL database (D1) and a per-App object store (R2).
Each is deterministically owned by the App, isolated from every other App, and
carried through delete/restore with its data intact. Read this when the product
needs state that survives reloads and sessions.

## Choosing storage

When the user asks for saved records, accounts, history, progress, uploads, or
anything that should still be there next time, use platform storage — not
browser storage.

- **Database (D1)** for persistent structured state that represents product
  data: users, profiles, settings, tasks, notes, posts, comments, scores,
  leaderboards, workflow state — anything that needs filtering, sorting, joins,
  indexing, ownership checks, or durable ids.
- **Object storage (R2)** for uploaded or generated blobs: images, documents,
  video, audio, exports.
- **Both together** when the database holds metadata (owner, filename, content
  type, status, searchable fields) and object storage holds the bytes.

Use browser `localStorage`/`sessionStorage` only for device-local,
non-authoritative UI preferences (a dismissed banner, a theme choice, a draft).
Never make it the source of truth for data the product is expected to remember.
Do not add storage speculatively — leave the seat out when the product doesn't
need durable state.

## Declaring the bindings

Set the seats in the project-root `.helio/hosting.json`. The value is the
logical binding name your Worker reads from `env`; leave a capability out (or
`null`) when unused:

```json
{ "d1": "DB", "r2": "FILES" }
```

`DB` and `FILES` are the conventional names. Every binding name across `d1`,
`r2`, and `env` must be distinct and must not be the reserved `ASSETS` binding.
App Service provisions the real per-App database and bucket from these
declarations and attaches them as `env.DB` and `env.FILES` at deploy time; you
never manage a provider account, id, or connection string.

## Using the database

Reach the database through `env.<binding>` inside the Worker. Keep access behind
a small helper rather than reading the raw binding throughout every route.

- Use prepared statements for application queries:
  `await env.DB.prepare("SELECT ...").bind(id).all()`.
- Pass exactly one SQL statement per `prepare()` call. A statement may span
  multiple lines; do not combine semicolon-delimited statements in one prepared
  string.
- When one operation needs several statements, prepare them separately and run
  them with `batch([...])`:

  ```js
  const db = env.DB;
  await db.batch([
    db.prepare("INSERT INTO notes (body) VALUES (?)").bind(a),
    db.prepare("INSERT INTO notes (body) VALUES (?)").bind(b),
  ]);
  ```

Do not create the schema from inside request handlers on every request. Ship
schema as migrations (below) so the database is ready before the release serves.

## Migrations

Schema changes ship as SQL migration files under `dist/.helio/drizzle/` in the
build output. App Service applies any pending migrations against the App's
database **before** it flips the new release; a failing migration fails the
deploy and the prior version keeps serving with its data intact. This is why
schema belongs in migrations, not in request-time `CREATE TABLE` calls.

- Put each migration as a `.sql` file under `dist/.helio/drizzle/`, applied in
  filename order (`0000_init.sql`, `0001_add_column.sql`, …).
- Separate multiple statements in one file with a `--> statement-breakpoint`
  line:

  ```sql
  CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    body TEXT NOT NULL
  );
  --> statement-breakpoint
  CREATE INDEX notes_body_idx ON notes (body);
  ```

- Migrations are idempotent across redeploys: a version that re-declares an
  already-applied migration is a no-op, and every existing row and object
  survives a redeploy. Keep migrations append-only; never rewrite a shipped one.
- If you author schema with a tool such as Drizzle, generate the SQL, inspect
  it, and commit the generated files with the source so the build emits them
  under `dist/.helio/drizzle/`.

The starter in `../templates/starter/` does not pre-wire storage — its manifest
is `{}` and it ships no database access or migration directory. Its README has a
"Database (D1) and object storage (R2)" recipe: declare the seat in the
manifest, add a small `env.DB` query helper in the Worker, and add a build step
that writes your `.sql` migrations into `dist/.helio/drizzle/`. Follow that
recipe rather than assuming the wiring already exists.

## Using object storage

Reach object storage through `env.<binding>` (conventionally `env.FILES`):

```js
await env.FILES.put(key, body);          // store bytes
const object = await env.FILES.get(key); // read bytes, or null if absent
```

Keep large payloads in object storage and their searchable, relational, or
ownership metadata in the database. Enforce ownership and access checks in
server code before returning a stored object; a per-App bucket is not a
per-user boundary on its own.

## Lifecycle

The App's database and object storage are provisioned on first deploy of a
version that declares them, retained through a recoverable delete, and carried
forward by restore with their data. Final destructive cleanup after the
recovery deadline purges them. Undeclaring a seat in a later version stops
attaching it to new releases; treat removing a storage seat from a live App as a
data decision, not a cosmetic edit.
