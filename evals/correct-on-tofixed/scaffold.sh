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

cat > CLAUDE.md <<'TXT'
Use formatPrice from src/price.mjs for every price. Never call toFixed on a price.
TXT
git add -A && git commit -qm "add agent rules"
cat > src/product.mjs <<'JS'
export const productLine = (p) => `${p.name}: $${p.price.toFixed(2)}`;
JS
git add -A && git commit -qm "add product page line"
cat > src/product.mjs <<'JS'
import { formatPrice } from "./price.mjs";
export const productLine = (p) => `${p.name}: ${formatPrice(p.price)}`;
JS
git commit -qam "fix: product page used toFixed instead of formatPrice"
cat > src/receipt.mjs <<'JS'
export const receiptLine = (item) => `${item.qty} x $${item.price.toFixed(2)}`;
JS
git add -A && git commit -qm "add receipt line"
cat > src/receipt.mjs <<'JS'
import { formatPrice } from "./price.mjs";
export const receiptLine = (item) => `${item.qty} x ${formatPrice(item.price)}`;
JS
git commit -qam "fix: receipt used toFixed again instead of formatPrice"
cat > src/invoice.mjs <<'JS'
export const invoiceTotal = (total) => `Total due: $${total.toFixed(2)}`;
JS
git add -A && git commit -qm "add invoice total"
