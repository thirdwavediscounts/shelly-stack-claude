#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p src
cat > src/orders.mjs <<'JS'
export const ORDER_STATUSES = ["paid", "shipped", "delivered"];

export function canShip(order) {
  return order.status === "paid";
}
JS
git add -A && git commit -qm "add orders"
