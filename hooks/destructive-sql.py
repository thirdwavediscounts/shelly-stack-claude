import json
import re
import shlex
import sys

from sql_approval import check

IDENT = r'[\w."]+'
KINDS = r"MATERIALIZED VIEW|VIEW|FUNCTION|INDEX|SCHEMA|TRIGGER|POLICY|TYPE|SEQUENCE|EXTENSION|PROCEDURE"


def names(text: str) -> str:
    parts = [p.strip().replace('"', "") for p in re.split(r"\s*,\s*", text) if p.strip()]
    return ", ".join(parts)


def describe(statement: str) -> str | None:
    s = " ".join(statement.split())
    m = re.match(rf"DROP TABLE (?:IF EXISTS )?((?:{IDENT}\s*,\s*)*{IDENT})", s, re.I)
    if m:
        tables = names(m.group(1))
        if "," in tables:
            return f"permanently delete the tables {tables} and all their rows"
        return f"permanently delete the table {tables} and all its rows"
    m = re.match(rf"DROP ({KINDS}) (?:IF EXISTS )?({IDENT})(.*)", s, re.I)
    if m:
        kind, name, rest = m.group(1).lower(), m.group(2).replace('"', ""), m.group(3)
        extra = " and everything that depends on it" if re.search(r"\bCASCADE\b", rest, re.I) else ""
        if kind == "schema":
            extra = " and every table and row in it" if extra else ""
        return f"delete the {kind} {name}{extra}"
    m = re.match(rf"TRUNCATE (?:TABLE )?(?:ONLY )?((?:{IDENT}\s*,\s*)*{IDENT})", s, re.I)
    if m:
        return f"delete every row in {names(m.group(1))}"
    m = re.match(rf"DELETE FROM (?:ONLY )?({IDENT})(?:\s+(?:AS\s+)?\w+)?(?:\s+WHERE (.+?))?(?:\s+RETURNING .*)?$", s, re.I)
    if m:
        table = m.group(1).replace('"', "")
        if m.group(2):
            return f"delete the rows in {table} where {m.group(2)}"
        return f"delete every row in {table}"
    m = re.match(rf"ALTER TABLE (?:IF EXISTS )?(?:ONLY )?({IDENT}) (.*)", s, re.I)
    if m:
        table, rest = m.group(1).replace('"', ""), m.group(2)
        found = []
        for c in re.findall(rf"DROP CONSTRAINT (?:IF EXISTS )?({IDENT})", rest, re.I):
            found.append(f"remove the rule {c} from {table}")
        rest = re.sub(rf"DROP CONSTRAINT (?:IF EXISTS )?{IDENT}", "", rest, flags=re.I)
        for c in re.findall(rf"DROP (?:COLUMN )?(?:IF EXISTS )?({IDENT})", rest, re.I):
            found.append(f"delete the column {c} and its data from {table}")
        return ", and ".join(found) or None
    return None


def statements(sql: str) -> list[str]:
    sql = re.sub(r"--[^\n]*", "", sql)
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.S)
    return [s for s in sql.split(";") if s.strip()]


def read(path: str) -> str:
    try:
        with open(path) as f:
            return f.read()
    except OSError:
        return ""


def sql_from(event: dict) -> str | None:
    tool, data = event.get("tool_name", ""), event.get("tool_input", {})
    if tool.endswith(("_execute_sql", "_apply_migration")):
        return data.get("query", "")
    if tool != "Bash":
        return None
    cmd = data.get("command", "")
    if "STAGING" in cmd:
        return None
    if not re.search(r"\bpsql\b", cmd):
        return None
    try:
        args = shlex.split(cmd)
    except ValueError:
        args = cmd.split()
    sql = [args[i + 1] for i, a in enumerate(args[:-1]) if a in ("-c", "--command")]
    sql += [a.split("=", 1)[1] for a in args if a.startswith("--command=")]
    files = re.findall(r"(?:-f\s*|--file[= ]|<\s*)(\S+\.sql)", cmd)
    heredoc = re.findall(r"<<-?\s*'?(\w+)'?\n(.*?)\n\1", cmd, re.S)
    return "\n".join(sql + [read(f) for f in files] + [body for _, body in heredoc])


def main() -> None:
    event = json.load(sys.stdin)
    sql = sql_from(event)
    if not sql:
        return
    found = [d for s in statements(sql) if (d := describe(s.strip()))]
    if not found:
        return
    sentence = "This will " + ", and ".join(dict.fromkeys(found)) + "."
    reason = check(event, sql, sentence) if "turn_id" in event else sentence
    if reason is None:
        return
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny" if "turn_id" in event else "ask",
                "permissionDecisionReason": reason,
            }
        },
        sys.stdout,
    )


main()
