#!/usr/bin/env python3
"""Local tickets under <repo>/tickets/. Frontmatter in <ID>.md is the source of truth; index.tsv is rebuilt from it."""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fcntl
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lint_ticket_text import lint  # noqa: E402

STATUSES = [
    "Backlog",
    "Triage",
    "Needs Investigation",
    "Ready for Agents",
    "In Progress",
    "Need Human",
    "Verifying Work",
    "Verifying Live",
    "In Review",
    "Done",
    "Canceled",
]
FIELDS = ["id", "title", "status", "parent", "app", "type", "priority", "labels", "branch", "pr", "created", "updated"]
SETTABLE = {"title", "app", "type", "priority", "labels", "branch", "pr"}
INDEX_COLUMNS = ["id", "title", "status", "parent", "app", "branch", "pr", "updated"]
LOG_COLUMNS = ["ts", "phase", "decision", "why", "evidence", "result"]
ROOT_ID = re.compile(r"^DEV-(\d+)$")
SUB_ID = re.compile(r"^(DEV-\d+)-(\d+)$")
PREFIX = "DEV"


class TicketError(Exception):
    pass


def repo_root() -> Path:
    override = os.environ.get("TICKETS_ROOT")
    if override:
        return Path(override).resolve()
    try:
        common = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
    except subprocess.CalledProcessError as e:
        raise TicketError("not inside a git repository; run from the target repo") from e
    common_path = Path(common)
    if common_path.name == ".git":
        return common_path.parent
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], check=True, capture_output=True, text=True)
    return Path(top.stdout.strip())


def tickets_dir() -> Path:
    return repo_root() / "tickets"


def assert_untracked(root: Path) -> None:
    probe = "tickets/index.tsv"
    tracked = subprocess.run(["git", "-C", str(root), "ls-files", "--", "tickets"], capture_output=True, text=True).stdout.strip()
    ignored = subprocess.run(["git", "-C", str(root), "check-ignore", "-q", probe]).returncode == 0
    if tracked or not ignored:
        raise TicketError(
            f"{root}/tickets/ would be tracked by git. Add `tickets/` to .gitignore or .git/info/exclude, then retry."
        )


@contextlib.contextmanager
def write_lock():
    root = repo_root()
    assert_untracked(root)
    tdir = root / "tickets"
    tdir.mkdir(exist_ok=True)
    with open(tdir / ".lock", "w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield tdir
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def today() -> str:
    return dt.date.today().isoformat()


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def folder_for(ticket_id: str) -> str:
    m = SUB_ID.match(ticket_id)
    if m:
        return m.group(1)
    if ROOT_ID.match(ticket_id):
        return ticket_id
    raise TicketError(f"bad ticket id {ticket_id!r}; expected {PREFIX}-<n> or {PREFIX}-<n>-<m>")


def md_path(tdir: Path, ticket_id: str) -> Path:
    return tdir / folder_for(ticket_id) / f"{ticket_id}.md"


def log_path(tdir: Path, ticket_id: str) -> Path:
    return tdir / folder_for(ticket_id) / f"{ticket_id}.tsv"


def parse(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        raise TicketError("ticket file has no frontmatter")
    end = text.index("\n---\n", 4)
    meta = {}
    for line in text[4:end].splitlines():
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    return meta, text[end + 5:]


def render(meta: dict[str, str], body: str) -> str:
    head = "\n".join(f"{k}: {meta.get(k, '')}".rstrip() for k in FIELDS)
    return f"---\n{head}\n---\n{body}"


def load(tdir: Path, ticket_id: str) -> tuple[dict[str, str], str]:
    path = md_path(tdir, ticket_id)
    if not path.exists():
        raise TicketError(f"{ticket_id} not found at {path}")
    return parse(path.read_text())


def save(tdir: Path, meta: dict[str, str], body: str) -> None:
    meta["updated"] = today()
    path = md_path(tdir, meta["id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(meta, body))


def cell(value: str) -> str:
    v = re.sub(r"[\t\r\n]+", " ", value or "").strip()
    return f"'{v}" if v[:1] in ("=", "+", "-", "@") else v


def append_log(tdir: Path, ticket_id: str, phase: str, decision: str, why: str, evidence: str, result: str) -> None:
    path = log_path(tdir, ticket_id)
    if not path.exists():
        path.write_text("\t".join(LOG_COLUMNS) + "\n")
    with open(path, "a") as fh:
        fh.write("\t".join([now()] + [cell(x) for x in (phase, decision, why, evidence, result)]) + "\n")


def all_tickets(tdir: Path) -> list[dict[str, str]]:
    metas = []
    for path in sorted(tdir.glob(f"{PREFIX}-*/{PREFIX}-*.md")):
        meta, _ = parse(path.read_text())
        metas.append(meta)

    def key(m: dict[str, str]) -> tuple[int, int]:
        parts = m["id"].split("-")
        return int(parts[1]), int(parts[2]) if len(parts) > 2 else 0

    return sorted(metas, key=key)


def reindex(tdir: Path) -> None:
    rows = ["\t".join(INDEX_COLUMNS)]
    for meta in all_tickets(tdir):
        rows.append("\t".join(cell(meta.get(c, "")) for c in INDEX_COLUMNS))
    (tdir / "index.tsv").write_text("\n".join(rows) + "\n")


def next_id(tdir: Path, parent: str | None) -> str:
    if parent:
        if not ROOT_ID.match(parent):
            raise TicketError(f"parent must be a top-level ticket like {PREFIX}-182, got {parent!r}")
        if not md_path(tdir, parent).exists():
            raise TicketError(f"parent {parent} not found")
        subs = [int(m.group(2)) for p in (tdir / parent).glob(f"{parent}-*.md") if (m := SUB_ID.match(p.stem))]
        return f"{parent}-{max(subs, default=0) + 1}"
    roots = [int(m.group(1)) for p in tdir.glob(f"{PREFIX}-*/{PREFIX}-*.md") if (m := ROOT_ID.match(p.stem))]
    return f"{PREFIX}-{max(roots, default=0) + 1}"


def check_text(text: str, kind: str) -> None:
    problems = lint(text, kind)
    if problems:
        raise TicketError("text fails the ticket lint:\n" + "\n".join(problems))


def check_status(status: str) -> str:
    if status not in STATUSES:
        raise TicketError(f"unknown status {status!r}; one of: {', '.join(STATUSES)}")
    return status


def read_body(args: argparse.Namespace) -> str:
    if getattr(args, "body_file", None):
        return Path(args.body_file).read_text()
    return sys.stdin.read()


def cmd_new(args: argparse.Namespace) -> None:
    body = read_body(args).strip() + "\n"
    check_text(body, "ticket")
    status = check_status(args.status)
    with write_lock() as tdir:
        ticket_id = next_id(tdir, args.parent)
        meta = {
            "id": ticket_id, "title": args.title, "status": status, "parent": args.parent or "",
            "app": args.app or "", "type": args.type or "", "priority": args.priority or "",
            "labels": args.labels or "", "branch": "", "pr": "", "created": today(),
        }
        save(tdir, meta, "\n" + body + "\n## Log\n")
        append_log(tdir, ticket_id, status, "created", args.why or "", args.evidence or "", status)
        reindex(tdir)
    print(ticket_id, md_path(tdir, ticket_id))


def cmd_show(args: argparse.Namespace) -> None:
    tdir = tickets_dir()
    path = md_path(tdir, args.id)
    if not path.exists():
        raise TicketError(f"{args.id} not found at {path}")
    print(f"# {path}\n")
    print(path.read_text())
    log = log_path(tdir, args.id)
    if log.exists():
        print(f"# {log}\n")
        print(log.read_text())
    subs = sorted((tdir / folder_for(args.id)).glob(f"{args.id}-*.md")) if ROOT_ID.match(args.id) else []
    for sub in subs:
        meta, _ = parse(sub.read_text())
        print(f"sub-ticket {meta['id']}\t{meta['status']}\t{meta['title']}")
    extras = [p for p in (tdir / folder_for(args.id)).iterdir() if p.suffix not in (".md", ".tsv")]
    for extra in extras:
        print(f"attachment {extra}")


def cmd_list(args: argparse.Namespace) -> None:
    tdir = tickets_dir()
    if not tdir.exists():
        print("no tickets/ folder")
        return
    print("\t".join(INDEX_COLUMNS))
    for meta in all_tickets(tdir):
        if args.status and meta["status"] not in args.status:
            continue
        if args.app and meta["app"] != args.app:
            continue
        print("\t".join(meta.get(c, "") for c in INDEX_COLUMNS))


def cmd_status(args: argparse.Namespace) -> None:
    status = check_status(args.status)
    with write_lock() as tdir:
        meta, body = load(tdir, args.id)
        old = meta["status"]
        meta["status"] = status
        save(tdir, meta, body)
        append_log(tdir, args.id, status, f"moved {old} to {status}", args.why, args.evidence or "", status)
        reindex(tdir)
    print(f"{args.id} {old} -> {status}")


def cmd_set(args: argparse.Namespace) -> None:
    updates = {}
    for pair in args.pairs:
        key, sep, value = pair.partition("=")
        if not sep or key not in SETTABLE:
            raise TicketError(f"bad field {pair!r}; settable: {', '.join(sorted(SETTABLE))}")
        updates[key] = value
    with write_lock() as tdir:
        meta, body = load(tdir, args.id)
        meta.update(updates)
        save(tdir, meta, body)
        for key, value in updates.items():
            append_log(tdir, args.id, meta["status"], f"set {key}", args.why or "", value, value)
        reindex(tdir)
    print(f"{args.id} " + " ".join(f"{k}={v}" for k, v in updates.items()))


def cmd_comment(args: argparse.Namespace) -> None:
    text = read_body(args).strip()
    check_text(text, "comment")
    with write_lock() as tdir:
        meta, body = load(tdir, args.id)
        if "\n## Log\n" not in body:
            body = body.rstrip() + "\n\n## Log\n"
        body = body.rstrip() + f"\n\n### {today()}\n\n{text}\n"
        save(tdir, meta, body)
        reindex(tdir)
    print(f"{args.id} comment added")


def cmd_log(args: argparse.Namespace) -> None:
    with write_lock() as tdir:
        meta, _ = load(tdir, args.id)
        append_log(tdir, args.id, meta["status"], args.decision, args.why, args.evidence, args.result)
    print(f"{args.id} logged")


def cmd_check(args: argparse.Namespace) -> None:
    tdir = tickets_dir()
    meta, body = load(tdir, args.id)
    check_status(meta["status"])
    check_text(body.split("\n## Log\n")[0], "ticket")
    print(f"{args.id} clean")


def cmd_reindex(args: argparse.Namespace) -> None:
    with write_lock() as tdir:
        for meta in all_tickets(tdir):
            check_status(meta["status"])
        reindex(tdir)
    print(tdir / "index.tsv")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="tickets.py")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("new", help="create a ticket or sub-ticket; body on stdin or --body-file")
    p.add_argument("--title", required=True)
    p.add_argument("--status", default="Triage")
    p.add_argument("--parent")
    p.add_argument("--app")
    p.add_argument("--type", choices=["Bug", "Feature", "Improvement"])
    p.add_argument("--priority", choices=["Urgent", "High", "Medium", "Low"])
    p.add_argument("--labels", help="comma-separated, e.g. Database")
    p.add_argument("--why")
    p.add_argument("--evidence")
    p.add_argument("--body-file")
    p.set_defaults(fn=cmd_new)

    p = sub.add_parser("show")
    p.add_argument("id")
    p.set_defaults(fn=cmd_show)

    p = sub.add_parser("list")
    p.add_argument("--status", action="append")
    p.add_argument("--app")
    p.set_defaults(fn=cmd_list)

    p = sub.add_parser("status")
    p.add_argument("id")
    p.add_argument("status")
    p.add_argument("--why", required=True)
    p.add_argument("--evidence")
    p.set_defaults(fn=cmd_status)

    p = sub.add_parser("set", help="set fields, e.g. branch=sean/x pr=https://github.com/o/r/pull/12")
    p.add_argument("id")
    p.add_argument("pairs", nargs="+")
    p.add_argument("--why")
    p.set_defaults(fn=cmd_set)

    p = sub.add_parser("comment", help="append a dated entry to the Log section; body on stdin or --body-file")
    p.add_argument("id")
    p.add_argument("--body-file")
    p.set_defaults(fn=cmd_comment)

    p = sub.add_parser("log", help="append one row to <ID>.tsv")
    p.add_argument("id")
    p.add_argument("--decision", required=True)
    p.add_argument("--why", required=True)
    p.add_argument("--evidence", default="")
    p.add_argument("--result", default="")
    p.set_defaults(fn=cmd_log)

    p = sub.add_parser("check", help="lint a hand-edited ticket body")
    p.add_argument("id")
    p.set_defaults(fn=cmd_check)

    p = sub.add_parser("reindex")
    p.set_defaults(fn=cmd_reindex)

    args = ap.parse_args(argv)
    try:
        args.fn(args)
    except TicketError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
