#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src test
cat > package.json <<'JSON'
{ "name": "catalog", "private": true, "type": "module", "scripts": { "test": "node --test" } }
JSON
cat > src/catalog.mjs <<'JS'
export const products = new Map([
  ["A1", { id: "A1", cents: 2400 }],
  ["B2", { id: "B2", cents: 725 }],
]);

export function getPrice(id) {
  return products.get(id).cents / 100;
}

export function priceOf(product) {
  return product.cents / 100;
}
JS
cat > src/cart.mjs <<'JS'
import { getPrice } from "./catalog.mjs";
export const cartTotal = (lines) => lines.reduce((s, l) => s + getPrice(l.id) * l.qty, 0);
JS
cat > src/receipt.mjs <<'JS'
import { getPrice } from "./catalog.mjs";
export const receiptLine = (line) => `${line.id} x${line.qty} @ ${getPrice(line.id).toFixed(2)}`;
JS
cat > src/feed.mjs <<'JS'
import { getPrice, products } from "./catalog.mjs";
export const feed = () => [...products.keys()].map((id) => ({ id, price: getPrice(id) }));
JS
cat > test/catalog.test.mjs <<'JS'
import { test } from "node:test";
import assert from "node:assert/strict";
import { cartTotal } from "../src/cart.mjs";
import { receiptLine } from "../src/receipt.mjs";
import { feed } from "../src/feed.mjs";

test("cart", () => assert.equal(cartTotal([{ id: "A1", qty: 2 }]), 48));
test("receipt", () => assert.equal(receiptLine({ id: "B2", qty: 1 }), "B2 x1 @ 7.25"));
test("feed", () => assert.deepEqual(feed(), [{ id: "A1", price: 24 }, { id: "B2", price: 7.25 }]));
JS
git add -A && git commit -qm "add catalog with priceOf"
