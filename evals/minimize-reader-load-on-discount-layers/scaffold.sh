#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src/discount test
cat > package.json <<'JSON'
{ "name": "shop", "private": true, "type": "module", "scripts": { "test": "node --test" } }
JSON
cat > src/checkout.mjs <<'JS'
import { discountFor } from "./discount/index.mjs";
export const checkout = (subtotal) => subtotal - discountFor(subtotal);
JS
cat > src/discount/index.mjs <<'JS'
import { DiscountService } from "./service.mjs";
const service = new DiscountService();
export const discountFor = (subtotal) => service.discountFor(subtotal);
JS
cat > src/discount/service.mjs <<'JS'
import { adapterDiscount } from "./adapter.mjs";
import { setRate } from "./state.mjs";
export class DiscountService {
  discountFor(subtotal) {
    setRate(subtotal > 100 ? 0.1 : 0);
    return adapterDiscount(subtotal);
  }
}
JS
cat > src/discount/adapter.mjs <<'JS'
import { providerDiscount } from "./provider.mjs";
export const adapterDiscount = (subtotal) => providerDiscount(subtotal);
JS
cat > src/discount/provider.mjs <<'JS'
import { currentRate } from "./state.mjs";
export const providerDiscount = (subtotal) => Math.round(subtotal * currentRate() * 100) / 100;
JS
cat > src/discount/state.mjs <<'JS'
let rate = 0;
export const setRate = (r) => { rate = r; };
export const currentRate = () => rate;
JS
cat > test/checkout.test.mjs <<'JS'
import { test } from "node:test";
import assert from "node:assert/strict";
import { checkout } from "../src/checkout.mjs";

test("no discount at 100", () => assert.equal(checkout(100), 100));
test("10% over 100", () => assert.equal(checkout(200), 180));
JS
git add -A && git commit -qm "add discount"
