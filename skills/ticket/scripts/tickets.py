#!/usr/bin/env python3
"""Tickets as GitHub issues, driven through the gh CLI. Status, priority, app and type are labels."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lint_ticket_text import lint  # noqa: E402

OPEN_STATUSES = {
    "Backlog": "backlog",
    "Triage": "triage",
    "Needs Investigation": "needs-investigation",
    "Ready": "ready",
    "In Progress": "in-progress",
    "Need Human": "need-human",
    "Verifying Work": "verifying-work",
    "Verifying Live": "verifying-live",
    "In Review": "in-review",
}
CLOSED_STATUSES = {"Done": "completed", "Canceled": "not_planned"}
STATUS_ALIASES = {"ready for agents": "Ready", "cancelled": "Canceled"}
TYPES = ["bug", "feature", "improvement"]
PRIORITIES = ["urgent", "high", "medium", "low"]
OWNER_LABEL = "sean"
MAX_BODY = 65536

LABEL_COLORS = {"status": "0e8a16", "priority": "d93f0b", "type": "5319e7", "app": "1d76db", "area": "fbca04"}


class TicketError(Exception):
    pass


def parse_status(value: str) -> str:
    key = value.strip().lower().removeprefix("status:")
    for name, slug in OPEN_STATUSES.items():
        if key in (name.lower(), slug):
            return name
    for name in CLOSED_STATUSES:
        if key == name.lower():
            return name
    if key in STATUS_ALIASES:
        return STATUS_ALIASES[key]
    raise TicketError(f"unknown status {value!r}; one of: {', '.join([*OPEN_STATUSES, *CLOSED_STATUSES])}")


def status_label(status: str) -> str:
    return f"status:{OPEN_STATUSES[status]}"


def label_names(issue: dict) -> list[str]:
    return [label["name"] for label in issue.get("labels", [])]


def status_of(issue: dict) -> str:
    if issue["state"].lower() == "closed":
        reason = (issue.get("state_reason") or issue.get("stateReason") or "").lower()
        return "Canceled" if reason == "not_planned" else "Done"
    found = [parse_status(n) for n in label_names(issue) if n.startswith("status:")]
    return found[0] if len(found) == 1 else ("none" if not found else "+".join(found))


def group_value(issue: dict, group: str) -> str:
    return ",".join(n.split(":", 1)[1] for n in label_names(issue) if n.startswith(f"{group}:"))


def with_group(labels: list[str], group: str, value: str | None) -> list[str]:
    kept = [n for n in labels if not n.startswith(f"{group}:")]
    return kept + [f"{group}:{value}"] if value else kept


def repo_from_remote() -> str:
    try:
        url = subprocess.run(["git", "remote", "get-url", "origin"], check=True, capture_output=True, text=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise TicketError("no --repo, no TICKETS_REPO, and no git origin remote here") from e
    m = re.search(r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?/?$", url)
    if not m:
        raise TicketError(f"origin {url!r} is not a GitHub remote; pass --repo owner/name")
    return m.group(1)


def resolve_repo(flag: str | None) -> str:
    return flag or os.environ.get("TICKETS_REPO") or repo_from_remote()


def app_folders() -> list[str]:
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], check=True, capture_output=True, text=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    apps = Path(top) / "apps"
    return sorted(p.name for p in apps.iterdir() if p.is_dir()) if apps.is_dir() else []


class Gh:
    """Reads always run. Writes run, or print the exact gh call under --dry-run."""

    def __init__(self, repo: str, dry_run: bool = False):
        self.repo = repo
        self.dry_run = dry_run

    def _run(self, args: list[str], stdin: str | None = None) -> str:
        r = subprocess.run(["gh", *args], input=stdin, capture_output=True, text=True)
        if r.returncode != 0:
            raise TicketError(f"gh {' '.join(args)} failed: {r.stderr.strip() or r.stdout.strip()}")
        return r.stdout

    def read(self, *args: str):
        return json.loads(self._run(list(args)) or "null")

    def api_get(self, path: str, paginate: bool = False):
        if paginate:
            pages = self.read("api", f"repos/{self.repo}/{path}", "--paginate", "--slurp")
            return [item for page in pages for item in page]
        return self.read("api", f"repos/{self.repo}/{path}")

    def write(self, method: str, path: str, payload: dict | None = None) -> dict | None:
        args = ["api", "-X", method, f"repos/{self.repo}/{path}"]
        body = json.dumps(payload, ensure_ascii=False, indent=2) if payload is not None else None
        if body is not None:
            args += ["--input", "-"]
        if self.dry_run:
            line = "gh " + shlex.join(args)
            print(f"{line} <<'JSON'\n{body}\nJSON" if body is not None else line)
            return None
        out = self._run(args, body)
        return json.loads(out) if out.strip() else {}

    def issue(self, number: int) -> dict:
        issue = self.api_get(f"issues/{number}")
        if "pull_request" in issue:
            raise TicketError(f"#{number} is a pull request, not an issue")
        return issue

    def comment(self, number: int, body: str) -> None:
        self.write("POST", f"issues/{number}/comments", {"body": body})


def check_text(text: str, kind: str) -> None:
    problems = lint(text, kind)
    if problems:
        raise TicketError("text fails the ticket lint:\n" + "\n".join(problems))


def fence_for(text: str) -> str:
    longest = max((len(m) for m in re.findall(r"`+", text)), default=0)
    return "`" * max(3, longest + 1)


def inline_attachment(name: str, text: str) -> str:
    fence = fence_for(text)
    return f"<details><summary>{name}</summary>\n\n{fence}\n{text.rstrip()}\n{fence}\n\n</details>"


def read_attachment(path: str) -> str:
    data = Path(path).read_bytes()
    try:
        if b"\0" in data:
            raise UnicodeDecodeError("utf-8", data, 0, 1, "NUL byte")
        return data.decode("utf-8")
    except UnicodeDecodeError:
        raise TicketError(
            f"{path} is binary and the GitHub API cannot upload files. Commit it to a branch and link it in the text."
        ) from None


def with_attachments(text: str, paths: list[str] | None) -> str:
    blocks = [inline_attachment(Path(p).name, read_attachment(p)) for p in paths or []]
    full = "\n\n".join([text.rstrip(), *blocks]) + "\n"
    if len(full) > MAX_BODY:
        raise TicketError(f"text is {len(full)} characters; GitHub caps a body at {MAX_BODY}. Link large files instead.")
    return full


def status_comment(old: str, new: str, why: str, evidence: str | None) -> str:
    lines = [f"**Status** · {old} → {new}", f"- Why: {why}"]
    if evidence:
        lines.append(f"- Evidence: {evidence}")
    return "\n".join(lines)


def decision_comment(status: str, decision: str, why: str, evidence: str | None, result: str | None) -> str:
    lines = [f"**Decision** · status {status}", decision, f"- Why: {why}"]
    if evidence:
        lines.append(f"- Evidence: {evidence}")
    if result:
        lines.append(f"- Result: {result}")
    return "\n".join(lines)


def read_body(args: argparse.Namespace) -> str:
    if getattr(args, "body_file", None):
        return Path(args.body_file).read_text()
    return sys.stdin.read()


def issue_number(value: str) -> int:
    m = re.fullmatch(r"#?(\d+)", value.strip())
    if not m:
        raise TicketError(f"bad issue {value!r}; expected N or #N")
    return int(m.group(1))


def cmd_new(gh: Gh, args: argparse.Namespace) -> None:
    text = read_body(args).strip()
    check_text(text, "ticket")
    status = parse_status(args.status)
    if status in CLOSED_STATUSES:
        raise TicketError("a new ticket starts open")
    labels = [OWNER_LABEL, status_label(status)]
    labels = with_group(labels, "app", args.app)
    labels = with_group(labels, "type", args.type)
    labels = with_group(labels, "priority", args.priority)
    labels += [n.strip() for n in (args.labels or "").split(",") if n.strip() and n.strip() not in labels]
    parent = issue_number(args.parent) if args.parent else None
    if parent is not None:
        gh.issue(parent)
    created = gh.write("POST", "issues", {"title": args.title, "body": with_attachments(text, args.attach), "labels": labels})
    if parent is not None:
        child_id = created["id"] if created else "<id of the new issue>"
        gh.write("POST", f"issues/{parent}/sub_issues", {"sub_issue_id": child_id})
    if created:
        print(f"#{created['number']} {created['html_url']}")


def cmd_status(gh: Gh, args: argparse.Namespace) -> None:
    number = issue_number(args.number)
    new = parse_status(args.status)
    body = status_comment("", new, args.why, args.evidence)
    check_text(body, "comment")
    issue = gh.issue(number)
    old = status_of(issue)
    labels = [n for n in label_names(issue) if not n.startswith("status:")]
    patch: dict = {"labels": labels}
    if new in CLOSED_STATUSES:
        patch.update(state="closed", state_reason=CLOSED_STATUSES[new])
    else:
        patch["labels"] = labels + [status_label(new)]
        if issue["state"].lower() == "closed":
            patch.update(state="open", state_reason="reopened")
    gh.write("PATCH", f"issues/{number}", patch)
    gh.comment(number, status_comment(old, new, args.why, args.evidence))
    if not gh.dry_run:
        print(f"#{number} {old} -> {new}")


SETTABLE = {"title", "app", "type", "priority", "labels", "branch", "pr"}


def cmd_set(gh: Gh, args: argparse.Namespace) -> None:
    number = issue_number(args.number)
    updates: dict[str, str] = {}
    for pair in args.pairs:
        key, sep, value = pair.partition("=")
        if not sep or key not in SETTABLE:
            raise TicketError(f"bad field {pair!r}; settable: {', '.join(sorted(SETTABLE))}")
        updates[key] = value.strip()
    if updates.get("type") and updates["type"].lower() not in TYPES:
        raise TicketError(f"type is one of {', '.join(TYPES)}")
    if updates.get("priority") and updates["priority"].lower() not in PRIORITIES:
        raise TicketError(f"priority is one of {', '.join(PRIORITIES)}")
    notes = []
    if "branch" in updates:
        notes.append(f"**Branch** · `{updates['branch']}`")
    if "pr" in updates:
        notes.append(f"**PR** · {updates['pr']}")
    issue = gh.issue(number)
    labels = label_names(issue)
    new_labels = labels
    for group in ("app", "type", "priority"):
        if group in updates:
            new_labels = with_group(new_labels, group, updates[group].lower() or None)
    for name in (n.strip() for n in updates.get("labels", "").split(",")):
        if name and name not in new_labels:
            new_labels = [*new_labels, name]
    patch: dict = {}
    if "title" in updates:
        patch["title"] = updates["title"]
    if new_labels != labels:
        patch["labels"] = new_labels
    if patch:
        gh.write("PATCH", f"issues/{number}", patch)
    if notes:
        gh.comment(number, "\n".join(notes))
    if not gh.dry_run:
        print(f"#{number} " + " ".join(f"{k}={v}" for k, v in updates.items()))


def cmd_comment(gh: Gh, args: argparse.Namespace) -> None:
    number = issue_number(args.number)
    text = read_body(args).strip()
    check_text(text, "comment")
    gh.comment(number, with_attachments(text, args.attach).rstrip("\n"))
    if not gh.dry_run:
        print(f"#{number} comment added")


def cmd_log(gh: Gh, args: argparse.Namespace) -> None:
    number = issue_number(args.number)
    issue = gh.issue(number)
    body = decision_comment(status_of(issue), args.decision, args.why, args.evidence, args.result)
    check_text(body, "comment")
    gh.comment(number, body)
    if not gh.dry_run:
        print(f"#{number} logged")


def cmd_check(gh: Gh, args: argparse.Namespace) -> None:
    number = issue_number(args.number)
    issue = gh.issue(number)
    check_text(issue.get("body") or "", "ticket")
    if issue["state"].lower() == "open" and status_of(issue) not in OPEN_STATUSES:
        raise TicketError(f"#{number} is open with status labels {status_of(issue)}; it needs exactly one")
    print(f"#{number} clean")


def cmd_list(gh: Gh, args: argparse.Namespace) -> None:
    wanted = [parse_status(s) for s in args.status or []]
    state = "all" if any(s in CLOSED_STATUSES for s in wanted) else "open"
    fields = "number,title,state,stateReason,labels,url"
    issues = gh.read("issue", "list", "--repo", gh.repo, "--label", OWNER_LABEL, "--state", state, "--limit", "1000", "--json", fields)
    print("number\tstatus\tapp\tpriority\ttitle")
    for issue in sorted(issues, key=lambda i: i["number"]):
        status = status_of(issue)
        if wanted and status not in wanted:
            continue
        if args.app and group_value(issue, "app") != args.app:
            continue
        print(f"#{issue['number']}\t{status}\t{group_value(issue, 'app')}\t{group_value(issue, 'priority')}\t{issue['title']}")


def cmd_show(gh: Gh, args: argparse.Namespace) -> None:
    number = issue_number(args.number)
    fields = "number,title,state,stateReason,labels,body,comments,parent,closedByPullRequestsReferences,url"
    issue = gh.read("issue", "view", str(number), "--repo", gh.repo, "--json", fields)
    subs = gh.api_get(f"issues/{number}/sub_issues?per_page=100")
    print(f"#{issue['number']} {issue['title']}")
    print(f"status: {status_of(issue)}")
    print(f"labels: {', '.join(label_names(issue))}")
    print(f"url: {issue['url']}")
    parent = issue.get("parent")
    print(f"parent: #{parent['number']} {parent['title']}" if parent else "parent: none")
    for pr in issue.get("closedByPullRequestsReferences") or []:
        print(f"pr: #{pr['number']} {pr.get('url', '')}".rstrip())
    for sub in subs:
        print(f"sub-issue: #{sub['number']}\t{status_of(sub)}\t{sub['title']}")
    print(f"\n{issue.get('body') or ''}".rstrip())
    for c in issue.get("comments") or []:
        author = (c.get("author") or {}).get("login", "")
        print(f"\n--- comment by {author} at {c.get('createdAt', '')}\n{c['body']}")


def desired_labels(apps: list[str]) -> dict[str, str]:
    names = [OWNER_LABEL, *(status_label(s) for s in OPEN_STATUSES), *(f"priority:{p}" for p in PRIORITIES),
             *(f"type:{t}" for t in TYPES), "area:database", *(f"app:{a}" for a in apps)]
    return {n: LABEL_COLORS.get(n.split(":", 1)[0], "ededed") for n in names}


def cmd_labels(gh: Gh, args: argparse.Namespace) -> None:
    if not args.ensure:
        raise TicketError("labels needs --ensure")
    existing = {label["name"] for label in gh.api_get("labels?per_page=100", paginate=True)}
    wanted = desired_labels(app_folders())
    missing = [n for n in wanted if n not in existing]
    for name in missing:
        gh.write("POST", "labels", {"name": name, "color": wanted[name]})
    print(f"{len(missing)} missing, {len(wanted) - len(missing)} already present")


def main(argv: list[str] | None = None) -> int:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--repo", help="owner/name; defaults to $TICKETS_REPO, then the origin remote")
    common.add_argument("--dry-run", action="store_true", help="print the gh write calls instead of running them")
    ap = argparse.ArgumentParser(prog="tickets.py")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name: str, fn, help_text: str | None = None) -> argparse.ArgumentParser:
        p = sub.add_parser(name, parents=[common], help=help_text)
        p.set_defaults(fn=fn)
        return p

    p = add("new", cmd_new, "create an issue; body on stdin or --body-file")
    p.add_argument("--title", required=True)
    p.add_argument("--status", default="Triage")
    p.add_argument("--parent", help="parent issue number")
    p.add_argument("--app")
    p.add_argument("--type", choices=TYPES, type=str.lower)
    p.add_argument("--priority", choices=PRIORITIES, type=str.lower)
    p.add_argument("--labels", help="comma-separated extra labels, e.g. area:database")
    p.add_argument("--attach", action="append", help="text file to inline; repeatable")
    p.add_argument("--body-file")

    p = add("show", cmd_show)
    p.add_argument("number")

    p = add("list", cmd_list)
    p.add_argument("--status", action="append")
    p.add_argument("--app")

    p = add("status", cmd_status)
    p.add_argument("number")
    p.add_argument("status")
    p.add_argument("--why", required=True)
    p.add_argument("--evidence")

    p = add("set", cmd_set, "branch=B and pr=URL post a comment; title, app, type, priority, labels edit the issue")
    p.add_argument("number")
    p.add_argument("pairs", nargs="+")

    p = add("comment", cmd_comment, "post a comment; text on stdin or --body-file")
    p.add_argument("number")
    p.add_argument("--attach", action="append")
    p.add_argument("--body-file")

    p = add("log", cmd_log, "post a decision comment")
    p.add_argument("number")
    p.add_argument("--decision", required=True)
    p.add_argument("--why", required=True)
    p.add_argument("--evidence")
    p.add_argument("--result")

    p = add("check", cmd_check, "lint the live issue body")
    p.add_argument("number")

    p = add("labels", cmd_labels, "create missing labels")
    p.add_argument("--ensure", action="store_true")

    args = ap.parse_args(argv)
    try:
        args.fn(Gh(resolve_repo(args.repo), args.dry_run), args)
    except TicketError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
