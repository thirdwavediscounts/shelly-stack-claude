#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src
cat > src/checkout.mjs <<'JS'
import { cartTotal } from "./cart.mjs";
import { taxFor } from "./tax.mjs";
import { reserve } from "./inventory.mjs";
import { charge } from "./payment.mjs";

export async function checkout(cart, customer) {
  const subtotal = cartTotal(cart.items);
  const tax = taxFor(subtotal, customer.state);
  for (const item of cart.items) reserve(item.sku, item.qty);
  await charge(customer.id, subtotal + tax);
  return { subtotal, tax, total: subtotal + tax };
}
JS
cat > src/cart.mjs <<'JS'
export const cartTotal = (items) => items.reduce((s, i) => s + i.price * i.qty, 0);
JS
cat > src/tax.mjs <<'JS'
const RATES = { CA: 0.0725, NY: 0.04, OR: 0 };
export const taxFor = (subtotal, state) => Math.round(subtotal * (RATES[state] ?? 0) * 100) / 100;
JS
cat > src/inventory.mjs <<'JS'
const stock = new Map();
export function reserve(sku, qty) {
  stock.set(sku, (stock.get(sku) ?? 10) - qty);
}
JS
cat > src/payment.mjs <<'JS'
export async function charge(customerId, amount) {
  if (amount <= 0) throw new Error("nothing to charge");
  return { customerId, amount };
}
JS
git add -A && git commit -qm "add checkout"
