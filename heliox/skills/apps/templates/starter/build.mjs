// Zero-dependency build for a Helio App.
//
// Assembles the deploy output under `dist/`:
//   - src/public/**   -> dist/**            (static assets, served by env.ASSETS)
//   - src/server/**   -> dist/server/**     (Worker modules; index.js is the entrypoint)
//
// The project-root `.helio/hosting.json` is packaged by heliox at deploy time,
// so this build does not touch `dist/.helio/`. When the App uses a database,
// write its migrations to `dist/.helio/drizzle/` here (see README).
//
// Run with: node build.mjs   (wired as `npm run build`).

import { cp, mkdir, rm } from "node:fs/promises";
import { existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(fileURLToPath(import.meta.url));
const dist = resolve(root, "dist");
const publicDir = resolve(root, "src/public");
const serverDir = resolve(root, "src/server");

await rm(dist, { recursive: true, force: true });
await mkdir(dist, { recursive: true });

if (existsSync(publicDir)) {
  await cp(publicDir, dist, { recursive: true });
}

await mkdir(resolve(dist, "server"), { recursive: true });
await cp(serverDir, resolve(dist, "server"), { recursive: true });

console.log("built dist/ (assets + Worker)");
