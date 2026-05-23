import { copyFileSync, existsSync, rmSync } from "node:fs";
import { join } from "node:path";

const clientDir = "dist/client";
const shell = join(clientDir, "_shell.html");
const index = join(clientDir, "index.html");

if (!existsSync(shell)) {
  console.error(`[postbuild-spa] ${shell} not found — did TanStack SPA prerender run?`);
  process.exit(1);
}

copyFileSync(shell, index);
console.log(`[postbuild-spa] Wrote ${index} from ${shell}`);

// Remove the now-stale legacy server dir so Vercel doesn't ship it
const serverDir = "dist/server";
if (existsSync(serverDir)) {
  rmSync(serverDir, { recursive: true, force: true });
  console.log(`[postbuild-spa] Removed ${serverDir}`);
}
