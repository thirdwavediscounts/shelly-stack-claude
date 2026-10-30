#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p public
cat > public/products.html <<'HTML'
<!doctype html>
<html>
<body>
<table id="products">
  <thead><tr><th>SKU</th><th>Name</th><th>Price</th></tr></thead>
  <tbody>
    <tr><td>A1</td><td>Desk lamp</td><td>24.00</td></tr>
    <tr><td>B2</td><td>Office chair</td><td>139.00</td></tr>
    <tr><td>C3</td><td>Monitor arm</td><td>59.00</td></tr>
    <tr><td>D4</td><td>Keyboard</td><td>45.00</td></tr>
  </tbody>
</table>
</body>
</html>
HTML
git add -A && git commit -qm "add products table"
