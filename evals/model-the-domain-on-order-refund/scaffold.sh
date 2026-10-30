#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src test
cat > package.json <<'JSON'
{ "name": "orders", "private": true, "type": "module", "scripts": { "test": "node --test" } }
JSON
cat > src/order.mjs <<'JS'
export const newOrder = () => ({ isPaid: false, isShipped: false, isCancelled: false });

export function pay(o) {
  if (o.isPaid || o.isCancelled) throw new Error("cannot pay");
  o.isPaid = true;
}

export function ship(o) {
  if (!o.isPaid || o.isShipped || o.isCancelled) throw new Error("cannot ship");
  o.isShipped = true;
}

export function cancel(o) {
  if (o.isShipped || o.isCancelled) throw new Error("cannot cancel");
  o.isCancelled = true;
}

export function label(o) {
  if (o.isCancelled) return "Cancelled";
  if (o.isShipped) return "Shipped";
  if (o.isPaid) return "Paid";
  return "New";
}
JS
cat > test/order.test.mjs <<'JS'
import { test } from "node:test";
import assert from "node:assert/strict";
import { newOrder, pay, ship, cancel, label } from "../src/order.mjs";

test("pay then ship", () => {
  const o = newOrder();
  pay(o);
  ship(o);
  assert.equal(label(o), "Shipped");
});
test("cannot ship unpaid", () => assert.throws(() => ship(newOrder())));
test("cancel new", () => {
  const o = newOrder();
  cancel(o);
  assert.equal(label(o), "Cancelled");
});
JS
git add -A && git commit -qm "add order lifecycle"
