#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src data test
cat > package.json <<'JSON'
{ "name": "shop", "private": true, "type": "module", "scripts": { "test": "node --test" } }
JSON
cat > data/products.csv <<'CSV'
sku;name;price
A1;Desk lamp;24.00
B2;Notebook;7,25
C3;Pen;1,50
CSV
cat > src/import.mjs <<'JS'
import { readFileSync } from "node:fs";

export function loadProducts(path = "data/products.csv") {
  const [, ...rows] = readFileSync(path, "utf8").trim().split("\n");
  return rows.map((row) => {
    const [sku, name, price] = row.split(";");
    return { sku, name, price: Number(price) };
  });
}
JS
cat > src/cart.mjs <<'JS'
export const cartTotal = (items) => "$" + items.reduce((s, i) => s + i.price * i.qty, 0).toFixed(2);
JS
cat > test/cart.test.mjs <<'JS'
import { test } from "node:test";
import assert from "node:assert/strict";
import { cartTotal } from "../src/cart.mjs";

test("total", () => assert.equal(cartTotal([{ price: 24, qty: 1 }]), "$24.00"));
JS
git add -A && git commit -qm "add product import and cart"
