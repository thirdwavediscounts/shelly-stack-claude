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
export const formatPrice = (n) => "$" + n.toFixed(2);
export const parsePrice = (s) => Number(s.replace("$", ""));
JS
cat > src/cart.mjs <<'JS'
export const cartTotal = (items) => items.reduce((s, i) => s + i.price * i.qty, 0);
JS
cat > src/tax.mjs <<'JS'
export const taxFor = (subtotal, rate) => Math.round(subtotal * rate * 100) / 100;
JS
cat > src/slug.mjs <<'JS'
export const slugify = (t) => t.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
export const truncate = (t, n) => (t.length > n ? t.slice(0, n) : t);
JS
cat > test/all.test.mjs <<'JS'
import { test } from "node:test";
import assert from "node:assert/strict";
import { formatPrice } from "../src/price.mjs";
import { cartTotal } from "../src/cart.mjs";
import { slugify } from "../src/slug.mjs";

test("formatPrice", () => assert.equal(formatPrice(2), "$2.00"));
test("cartTotal", () => assert.equal(cartTotal([{ price: 2, qty: 3 }]), 6));
test("slugify", () => assert.equal(slugify("Hello World!"), "hello-world"));
JS
git add -A && git commit -qm "add shop modules"
