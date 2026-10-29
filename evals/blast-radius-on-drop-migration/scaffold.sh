#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p supabase/migrations src
cat > supabase/migrations/20260101000000_orders.sql <<'SQL'
CREATE TABLE public.orders (
  id bigint PRIMARY KEY,
  sku text NOT NULL,
  total_cents integer NOT NULL,
  legacy_note text
);
SQL
cat > src/orders.mjs <<'JS'
export function orderSummary(order) {
  return `${order.sku}: ${order.total_cents / 100}`;
}
JS
git add -A && git commit -qm "add orders"
