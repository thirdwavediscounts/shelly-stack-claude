#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src
cat > src/order.mjs <<'JS'
export const newOrder = () => ({ status: "created" });

export function pay(order) {
  if (order.status !== "created") throw new Error("already paid");
  order.status = "paid";
}

export function ship(order) {
  if (order.status === "cancelled") throw new Error("cancelled");
  order.status = "shipped";
}

export function cancel(order) {
  if (order.status === "shipped") throw new Error("already shipped");
  order.status = "cancelled";
}
JS
git add -A && git commit -qm "add order flow"
