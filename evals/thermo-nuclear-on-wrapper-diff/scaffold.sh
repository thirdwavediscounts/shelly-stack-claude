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

git checkout -qb feature/price-service
cat > src/priceService.mjs <<'JS'
import { formatPrice } from "./price.mjs";

export class PriceService {
  constructor(mode = "new") {
    this.mode = mode;
  }

  format(amount) {
    if (this.mode === "legacy") {
      return formatPrice(amount);
    } else if (this.mode === "new") {
      return formatPrice(amount);
    }
    return formatPrice(amount);
  }
}
JS
cat > src/cart.mjs <<'JS'
import { PriceService } from "./priceService.mjs";

const prices = new PriceService("new");

export function cartTotal(items) {
  return prices.format(items.reduce((sum, item) => sum + item.price * item.qty, 0));
}
JS
git add -A && git commit -qm "add PriceService"
