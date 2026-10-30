#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src test
cat > package.json <<'JSON'
{ "name": "shop", "private": true, "type": "module", "scripts": { "test": "node --test" } }
JSON
cat > src/price.mjs <<'JS'
export function formatPrice(amount) {
  return "$" + amount.toFixed(2);
}
JS
cat > src/cart.mjs <<'JS'
import { formatPrice } from "./price.mjs";

export function cartTotal(items) {
  return formatPrice(items.reduce((sum, item) => sum + item.price * item.qty, 0));
}
JS
cat > test/price.test.mjs <<'JS'
import { test } from "node:test";
import assert from "node:assert/strict";
import { formatPrice } from "../src/price.mjs";
import { cartTotal } from "../src/cart.mjs";

test("formats cents", () => {
  assert.equal(formatPrice(12.5), "$12.50");
});

test("cart total multiplies by qty", () => {
  assert.equal(cartTotal([{ price: 6.25, qty: 2 }]), "$12.50");
});
JS
git add -A && git commit -qm "add formatPrice and cartTotal"

cat > src/price.mjs <<'JS'
export function formatPrice(amount) {
  return "$" + amount;
}
JS
git commit -qam "simplify formatPrice"

git checkout -qb fix-price
git checkout -q HEAD~1 -- src/price.mjs
git commit -qam "fix: restore two-decimal prices"
cat >> test/price.test.mjs <<'JS'

test("formats zero", () => {
  assert.equal(formatPrice(0), "$0.00");
});
JS
git commit -qam "test: format zero"
