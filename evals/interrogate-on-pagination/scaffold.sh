#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src
cat > package.json <<'JSON'
{ "name": "list", "private": true, "type": "module" }
JSON
cat > src/page.mjs <<'JS'
export function paginate(items, page, size) {
  return items.slice(page * size, page * size + size);
}
JS
git add -A && git commit -qm "add paginate (0-based pages)"
git checkout -qb feature/one-based-pages
cat > src/page.mjs <<'JS'
export function paginate(items, page, size) {
  if (page < 1) throw new RangeError("page starts at 1");
  return items.slice(page * size, page * size + size);
}
JS
git commit -qam "pages are now 1-based: page 1 is the first page"
