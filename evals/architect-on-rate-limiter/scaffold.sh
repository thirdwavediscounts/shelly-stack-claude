#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src
cat > package.json <<'JSON'
{ "name": "api", "private": true, "type": "module" }
JSON
cat > src/api.mjs <<'JS'
const routes = {
  "/orders": () => ({ status: 200, body: "orders" }),
  "/products": () => ({ status: 200, body: "products" }),
};

export function handle(request) {
  const route = routes[request.path];
  if (!route) return { status: 404, body: "not found" };
  return route(request);
}
JS
git add -A && git commit -qm "add api router"
