#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src test
cat > package.json <<'JSON'
{ "name": "shop", "private": true, "type": "module", "scripts": { "test": "node --test" } }
JSON
cat > src/cart.mjs <<'JS'
export function cartTotal(items) {
  return "$" + items.reduce((sum, item) => sum + item.price, 0).toFixed(2);
}
JS
cat > test/cart.test.mjs <<'JS'
import { test } from "node:test";
import assert from "node:assert/strict";
import { cartTotal } from "../src/cart.mjs";

test("one item", () => assert.equal(cartTotal([{ price: 5, qty: 1 }]), "$5.00"));
JS
git add -A && git commit -qm "add cartTotal"
