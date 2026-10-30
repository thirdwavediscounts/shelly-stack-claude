import json
import os
import re
import shlex
import sys

ALLOWED_NAMES = {"claude.md", "agents.md", "claude.local.md", "agents.local.md", "glossary.md", "glossary-map.md"}
ALLOWED_DIRS = ("/skills/", "/agents/", "/evals/", "/docs/adr/", "/.claude/rules/")
CAN_WRITE = re.compile(r"(?:>|\b(?:touch|tee|cp|mv|install)\b|\bopen\s*\(|\.write(?:_text|_bytes)?\s*\()")
UNKNOWN = "\0"


def allowed(path: str) -> bool:
    if not path.lower().endswith((".md", ".mdx")):
        return True
    if os.path.exists(path):
        return True
    if os.path.basename(path).lower() in ALLOWED_NAMES:
        return True
    if any(d in path for d in ALLOWED_DIRS):
        return True
    claude_home = os.path.join(os.path.expanduser("~"), ".claude") + os.sep
    return os.path.abspath(path).startswith(claude_home)


def paths(event: dict, cwd: str) -> list[str]:
    data = event.get("tool_input", {})
    if event.get("tool_name") == "Write":
        return [data.get("file_path", "")]
    command = data.get("command", "")
    if event.get("tool_name") == "apply_patch":
        return re.findall(r"^\*\*\* (?:Add|Update) File: (.+)$", command, re.M)
    if event.get("tool_name") != "Bash":
        return []
    patches = re.findall(r"^\*\*\* (?:Add|Update) File: (.+)$", command, re.M)
    if not CAN_WRITE.search(command):
        return patches
    names = dict(os.environ, **dict(re.findall(r"(?:^|[\s;&|])([A-Za-z_]\w*)=([^\s;&|]+)", command)))
    command = re.sub(r"\$\{?([A-Za-z_]\w*)\}?", lambda m: names.get(m.group(1), UNKNOWN), command)
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace = " \t\r"
        tokens = list(lexer) + ["\n"]
    except ValueError:
        return []
    found = patches
    base = cwd
    program = None
    args: list[str] = []
    redirect = False
    for token in tokens:
        if token in (";", "&&", "||", "|", "\n"):
            if program == "cd" and args:
                base = os.path.join(base, os.path.expanduser(args[0]))
            elif program in ("cp", "mv", "install") and args:
                found.append(os.path.join(base, args[-1]))
            elif program in ("touch", "tee"):
                found += [os.path.join(base, a) for a in args]
            program, args, redirect = None, [], False
        elif token in (">", ">>", ">&"):
            redirect = True
        elif redirect:
            found.append(os.path.join(base, token))
            redirect = False
        elif program is None:
            if not re.fullmatch(r"[A-Za-z_]\w*=.*", token):
                program = os.path.basename(token)
        elif not token.startswith("-"):
            args.append(token)
    found = [p for p in found if UNKNOWN not in p]
    if re.search(r"\bopen\s*\([^\n]*[\"'](?:w|a|x)[+bt]*[\"']|\.write(?:_text|_bytes)?\s*\(", command):
        dirs = [base] + [d for d in re.findall(r"[\"'](/[^\"'\n]*)[\"']", command) if os.path.isdir(d)]
        for name in re.findall(r"[\"']([^\"'\n]+\.mdx?)[\"']", command, re.I):
            if re.search(r"[*?\[]", name):
                continue
            homes = [os.path.join(d, name) for d in dirs]
            found.append(next((p for p in homes if os.path.exists(p)), homes[0]))
    return found


def main() -> None:
    event = json.load(sys.stdin)
    cwd = event.get("cwd", os.getcwd())
    blocked = [p for p in paths(event, cwd) if not allowed(os.path.abspath(os.path.join(cwd, p)))]
    if not blocked:
        return
    path = blocked[0]
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    f"Blocked new file {path}: no new .md files. Code is the source of truth "
                    "and git is the history. Put the content in code, a script, or a skill, "
                    "or ask the user before creating it."
                ),
            }
        },
        sys.stdout,
    )


main()
