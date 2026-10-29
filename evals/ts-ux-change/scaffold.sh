#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src
cat > package.json <<'JSON'
{ "name": "summary", "private": true, "type": "module", "devDependencies": { "typescript": "5.9.3" } }
JSON
cat > tsconfig.json <<'JSON'
{ "compilerOptions": { "strict": true, "target": "es2022", "module": "es2022", "noEmit": true }, "include": ["src"] }
JSON
cat > src/summary.ts <<'TS'
export type Row = { sku: string; title: string; labels: string[]; qty: number };

export function renderSummary(rows: Row[]): string {
  const body = rows
    .map((row) => `<tr><td>${row.sku}</td><td>${row.title} ${row.labels.join(" ")}</td><td>${row.qty}</td></tr>`)
    .join("");
  return `<table><tr><th>SKU</th><th>Title</th><th>Qty</th></tr>${body}</table>`;
}
TS
git add -A && git commit -qm "add summary page"
