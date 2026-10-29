import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shlex
import sys
from contextlib import contextmanager


@contextmanager
def approval_state(event: dict, create=False):
    import fcntl

    session = event.get("session_id")
    directory = os.environ.get("PLUGIN_DATA")
    if not session or not event.get("turn_id") or not directory:
        raise ValueError("Missing Codex session or plugin data directory")
    directory = Path(directory) / "sql-approvals"
    if create:
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = directory / (hashlib.sha256(session.encode()).hexdigest() + ".json")
    flags = os.O_RDWR | (os.O_CREAT if create else 0)
    with os.fdopen(os.open(path, flags, 0o600), "r+") as file:
        fcntl.flock(file, fcntl.LOCK_EX)
        state = json.loads(file.read() or "{}")
        if not isinstance(state, dict):
            raise ValueError("Invalid approval state")
        yield state
        file.seek(0)
        file.truncate()
        json.dump(state, file)
        file.flush()


def fingerprint(event: dict, sql: str) -> str:
    data = event["tool_input"]
    environment = {}
    if event["tool_name"] == "Bash":
        command = data["command"]
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace = " \t\r"
        args = list(lexer)
        connection_args = [arg for i, arg in enumerate(args[1:], 1)
                           if args[i - 1] not in ("-c", "--command", "-f", "--file")
                           and not arg.startswith(("--command=", "--file="))]
        if (not args or Path(args[0]).name != "psql"
                or any(re.fullmatch(r"[;&|<>\n]+", arg) for arg in args)
                or re.search(r"`|\$\(", command)
                or any(re.search(r"\bservice\s*=", os.path.expandvars(arg)) for arg in connection_args)
                or os.environ.get("PGSERVICE")):
            raise ValueError("Use a direct psql command without shell operators or a connection service")
        variables = re.findall(r"\$\{(\w+)\}|\$(\w+)", command)
        for pair in variables:
            name = pair[0] or pair[1]
            if name not in os.environ:
                raise ValueError(f"Connection variable {name} is unavailable to the hook")
            environment[name] = os.environ[name]
        environment.update({key: value for key, value in os.environ.items() if key.startswith("PG")})
    operation = [event["tool_name"], data, sql, event.get("cwd"), environment]
    return hashlib.sha256(json.dumps(operation, sort_keys=True).encode()).hexdigest()


def check(event: dict, sql: str, sentence: str) -> str | None:
    try:
        operation = fingerprint(event, sql)
    except (ValueError, KeyError, TypeError):
        return sentence + " Use a direct psql command with connection variables available to the hook to request approval."
    try:
        with approval_state(event, create=True) as state:
            if state.get("operation") == operation and state.get("approved_turn") == event["turn_id"]:
                state.clear()
                return None
            if state.get("operation") != operation or state.get("approved_turn"):
                state.clear()
                state.update(operation=operation, code=secrets.token_hex(6), sentence=sentence)
            return sentence + f' Ask the user to reply exactly "approve SQL {state["code"]}" to run this operation once.'
    except (ImportError, OSError, ValueError, KeyError, TypeError):
        return sentence + " SQL approval could not be recorded safely. Keep this command blocked."


def submit(event: dict) -> str | None:
    if "turn_id" not in event:
        return None
    match = re.fullmatch(r"approve SQL ([0-9a-f]{12})", event.get("prompt", "").strip(), re.I)
    try:
        with approval_state(event) as state:
            if state.get("approved_turn"):
                state.clear()
            if match and state.get("code") == match[1].lower():
                state["approved_turn"] = event["turn_id"]
                return (
                    state["sentence"] + " The user approved this operation once for this turn. "
                    "Retry the exact blocked tool call without changing its command, arguments, or database."
                )
            if match:
                return "SQL approval was not accepted. Ask for the current confirmation code; do not run the SQL."
    except FileNotFoundError:
        return "SQL approval was not accepted. Request a current confirmation code." if match else None
    except (ImportError, OSError, ValueError, KeyError, TypeError):
        return "SQL approval state is unavailable. Keep destructive SQL blocked."
    return None


if __name__ == "__main__":
    message = submit(json.load(sys.stdin))
    if message:
        print(message)
