#!/bin/bash
set -e
git init -q -b main .
git config user.email dev@example.com
git config user.name Dev
mkdir -p bin
cat > package.json <<'JSON'
{ "name": "todo", "version": "1.2.0", "private": true, "type": "module", "bin": { "todo": "bin/todo.mjs" } }
JSON
cat > bin/todo.mjs <<'JS'
#!/usr/bin/env node
import { existsSync, readFileSync, writeFileSync } from "node:fs";

const file = process.env.TODO_FILE ?? "todos.json";
const load = () => (existsSync(file) ? JSON.parse(readFileSync(file, "utf8")) : []);
const save = (todos) => writeFileSync(file, JSON.stringify(todos, null, 2));
const [command, ...rest] = process.argv.slice(2);

if (command === "--version") {
  console.log("todo 1.2.0");
} else if (command === "add") {
  const todos = load();
  const id = todos.length + 1;
  todos.push({ id, text: rest.join(" "), done: false });
  save(todos);
  console.log(`added #${id}`);
} else if (command === "list") {
  for (const t of load()) console.log(`${t.done ? "[x]" : "[ ]"} #${t.id} ${t.text}`);
} else if (command === "done") {
  const todos = load();
  const todo = todos.find((t) => t.id === Number(rest[0]));
  if (!todo) {
    console.error(`no todo #${rest[0]}`);
    process.exit(1);
  }
  todo.done = true;
  save(todos);
  console.log(`completed #${todo.id}`);
} else {
  console.error("usage: todo add <text> | list | done <id> | --version");
  process.exit(2);
}
JS
chmod +x bin/todo.mjs
git add -A && git commit -qm "add todo CLI"
