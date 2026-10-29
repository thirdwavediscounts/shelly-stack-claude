#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src
cat > package.json <<'JSON'
{ "name": "shop", "private": true, "type": "module", "scripts": { "test": "node --test" } }
JSON
cat > src/price.mjs <<'JS'
export function formatPrice(amount) {
  return "$" + amount;
}
JS
cat > src/price.test.mjs <<'JS'
import { test } from "node:test";
import assert from "node:assert/strict";
import { formatPrice } from "./price.mjs";

test("whole dollars", () => {
  assert.equal(formatPrice(12), "$12.00");
});
JS
cat > src/cart.mjs <<'JS'
export function cartTotal(items) {
  const total = items.reduce((sum, item) => sum + item.price * item.qty, 0);
  return "$" + total;
}
JS
git add -A && git commit -qm "add formatPrice and cartTotal"
