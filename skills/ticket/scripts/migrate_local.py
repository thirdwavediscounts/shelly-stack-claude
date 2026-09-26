#!/usr/bin/env python3
"""Plan, and with --execute run, the move of open local tickets and open Linear issues to GitHub issues.

Dry run is the default: it prints a readable plan and writes every planned payload to --plan-json.
--execute creates the issues through gh and records progress in --mapping, so a rerun resumes
without creating anything twice."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lint_ticket_text import lint  # noqa: E402
from tickets import (  # noqa: E402
    CLOSED_STATUSES, MAX_BODY, OPEN_STATUSES, OWNER_LABEL, PRIORITIES, TYPES, Gh, TicketError,
    decision_comment, inline_attachment, parse_status, resolve_repo, status_comment, status_label,
)

LOCAL_ID = re.compile(r"^DEV-(\d+)(?:-(\d+))?$")
BARE_REF = re.compile(r"(?<![\w/\[:-])DEV-\d+(?:-\d+)?(?![\w-]|\.\w)")
PLACEHOLDER = re.compile(r"\{\{ref:(local|linear):(DEV-\d+(?:-\d+)?)\}\}")
ISSUE_TAG = re.compile(r'<issue\b[^>]*?href="([^"]*)"[^>]*>\s*(DEV-\d+)\s*</issue>')
PR_TAG = re.compile(r'<pull-request\b[^>]*?href="([^"]*)"[^>]*>(.*?)</pull-request>', re.S)
GH_REF = re.compile(r"thirdwavediscounts/([\w.-]+?)(?:#|/pull/)(\d+)")
LINEAR_CLOSED = {"completed", "canceled", "duplicate"}
LINEAR_TYPE_FALLBACK = {"triage": "Triage", "backlog": "Backlog", "unstarted": "Ready", "started": "In Progress",
                        "completed": "Done", "canceled": "Canceled", "duplicate": "Canceled"}
COMMENT_ROOM = MAX_BODY - 500


@dataclass
class Refs:
    converted: int = 0
    linked: int = 0
    prs: int = 0
    unresolved: list[str] = field(default_factory=list)


@dataclass
class Planned:
    key: str
    title: str
    status: str
    labels: list[str]
    parent: str | None
    body: str
    comments: list[str]
    close: str | None
    inlined: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    refs: Refs = field(default_factory=Refs)
    notes: list[str] = field(default_factory=list)


def marker(key: str, comment: int | None = None) -> str:
    return f"<!-- migrated:{key}{'' if comment is None else f':c{comment}'} -->"


def outside_code(text: str, fn) -> str:
    """Apply fn to prose segments only: fenced blocks and inline code pass through unchanged."""
    out, fenced = [], False
    for line in text.split("\n"):
        if line.strip().startswith("```"):
            fenced = not fenced
            out.append(line)
            continue
        if fenced:
            out.append(line)
            continue
        parts = re.split(r"(`[^`]*`)", line)
        out.append("".join(p if p.startswith("`") else fn(p) for p in parts))
    return "\n".join(out)


def convert(text: str, own: str, migrating: dict[str, set[str]], repo_name: str, refs: Refs, linear_base: str | None = None) -> str:
    """Rewrites refs to migrating tickets as placeholders. An unmigrated Linear ref becomes a Linear link;
    an unmigrated local ref stays as text and counts as unresolved."""
    def issue_tag(m: re.Match) -> str:
        href, ident = m.group(1), m.group(2)
        if ident in migrating["linear"]:
            refs.converted += 1
            return "{{ref:linear:%s}}" % ident
        refs.linked += 1
        return f"[{ident}]({href})"

    def pr_tag(m: re.Match) -> str:
        href, label = m.group(1), m.group(2).strip()
        found = GH_REF.search(label) or GH_REF.search(href)
        refs.prs += 1
        if not found:
            return f"[{label}]({href})"
        return f"#{found.group(2)}" if found.group(1) == repo_name else f"thirdwavediscounts/{found.group(1)}#{found.group(2)}"

    def bare(segment: str) -> str:
        def one(m: re.Match) -> str:
            if m.group(0) in migrating[own]:
                refs.converted += 1
                return "{{ref:%s:%s}}" % (own, m.group(0))
            if own == "linear" and linear_base:
                refs.linked += 1
                return f"[{m.group(0)}]({linear_base}/{m.group(0)})"
            refs.unresolved.append(m.group(0))
            return m.group(0)
        return BARE_REF.sub(one, segment)

    text = PR_TAG.sub(pr_tag, ISSUE_TAG.sub(issue_tag, text))
    return outside_code(text, bare)


def split_attachment(name: str, text: str) -> list[str]:
    whole = inline_attachment(name, text)
    if len(whole) <= COMMENT_ROOM:
        return [whole]
    lines, chunks, current = text.splitlines(keepends=True), [], ""
    for line in lines:
        if current and len(current) + len(line) > COMMENT_ROOM - 200:
            chunks.append(current)
            current = ""
        current += line
    chunks.append(current)
    return [inline_attachment(f"{name}, part {i} of {len(chunks)}", c) for i, c in enumerate(chunks, 1)]


def parse_md(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text()
    end = text.index("\n---\n", 4)
    meta = {}
    for line in text[4:end].splitlines():
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip()
    return meta, text[end + 5:]


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    rows = path.read_text().splitlines()
    head = rows[0].split("\t")
    return [dict(zip(head, r.split("\t") + [""] * len(head))) for r in rows[1:] if r.strip()]


def id_key(ident: str) -> tuple[int, int]:
    m = LOCAL_ID.match(ident)
    return int(m.group(1)), int(m.group(2) or 0)


def owner_of(filename: str, ids: list[str], folder: str) -> str:
    matches = [i for i in ids if filename.startswith(i + ".")]
    return max(matches, key=len) if matches else folder


def status_name(value: str) -> str:
    try:
        return parse_status(value)
    except TicketError:
        return value


def base_labels(status: str) -> list[str]:
    return [OWNER_LABEL] + ([status_label(status)] if status in OPEN_STATUSES else [])


def local_tickets(tdir: Path, apps: set[str], repo_name: str, migrating: dict[str, set[str]]) -> tuple[list[Planned], list[str]]:
    metas: dict[str, tuple[dict[str, str], str, Path]] = {}
    for path in sorted(tdir.glob("DEV-*/DEV-*.md")):
        meta, body = parse_md(path)
        metas[meta["id"]] = (meta, body, path.parent)
    keep = {i for i, (m, _, _) in metas.items() if status_name(m["status"]) not in CLOSED_STATUSES}
    for ident in list(keep):
        parent = metas[ident][0].get("parent")
        while parent and parent in metas:
            keep.add(parent)
            parent = metas[parent][0].get("parent")
    migrating["local"] = keep
    attachments: dict[str, list[Path]] = {}
    for folder in sorted({p for _, _, p in metas.values()}):
        ids = [i for i in metas if metas[i][2] == folder]
        for f in sorted(folder.iterdir()):
            if f.suffix not in (".md", ".tsv") and not f.name.startswith("."):
                attachments.setdefault(owner_of(f.name, ids, folder.name), []).append(f)

    planned, dropped = [], []
    for ident in sorted(metas, key=id_key):
        meta, raw, folder = metas[ident]
        if ident not in keep:
            dropped += [f"{p.parent.name}/{p.name}" for p in attachments.get(ident, [])]
            continue
        refs = Refs()
        status = status_name(meta["status"])
        prose, _, log = raw.partition("\n## Log\n")
        labels = base_labels(status)
        if meta.get("priority", "").lower() in PRIORITIES:
            labels.append(f"priority:{meta['priority'].lower()}")
        if meta.get("app"):
            labels.append(f"app:{meta['app']}")
        if meta.get("type", "").lower() in TYPES:
            labels.append(f"type:{meta['type'].lower()}")
        notes = []
        if meta.get("app") and meta["app"] not in apps:
            notes.append(f"app {meta['app']!r} has no apps/ folder")
        for extra in filter(None, (x.strip() for x in meta.get("labels", "").split(","))):
            if extra.lower() == "database":
                labels.append("area:database")
            else:
                notes.append(f"label {extra!r} has no GitHub mapping")
        history: list[tuple[str, str]] = []
        for date, entry in re.findall(r"^### (\d{4}-\d{2}-\d{2})\n(.*?)(?=^### \d{4}-\d{2}-\d{2}\n|\Z)", log, re.S | re.M):
            if entry.strip():
                history.append((date, f"{entry.strip()}\n\n<sub>Local log entry, {date}</sub>"))
        for row in read_tsv(folder / f"{ident}.tsv"):
            moved = re.fullmatch(r"moved (.+) to (.+)", row.get("decision", ""))
            if moved:
                text = status_comment(status_name(moved.group(1)), status_name(moved.group(2)), row["why"] or "not recorded", row["evidence"])
            else:
                text = decision_comment(status_name(row["phase"]), row["decision"], row["why"] or "not recorded", row["evidence"], row["result"])
            history.append((row["ts"], f"{text}\n\n<sub>Local decision log, {row['ts']}</sub>"))
        history.sort(key=lambda h: h[0])
        comments = [convert(text, "local", migrating, repo_name, refs) for _, text in history]
        inlined, skipped = [], []
        for f in attachments.get(ident, []):
            try:
                text = f.read_bytes().decode("utf-8")
                if "\0" in text:
                    raise UnicodeDecodeError("utf-8", b"", 0, 1, "NUL")
            except UnicodeDecodeError:
                skipped.append(f"{folder.name}/{f.name}, binary, {f.stat().st_size // 1024} KB")
                continue
            parts = split_attachment(f.name, text)
            comments += parts
            inlined.append(f"{f.name}, {len(text) // 1024} KB" + (f", {len(parts)} comments" if len(parts) > 1 else ""))
        if skipped:
            comments.append("Attachments not migrated. The GitHub API cannot upload binary files, so they stay in the local tickets folder.\n\n"
                            + "\n".join(f"- `{s.split(',')[0]}`" for s in skipped))
        footer = f"<sub>Migrated from local ticket {ident}</sub>\n{marker('local:' + ident)}"
        body = convert(prose.strip(), "local", migrating, repo_name, refs) + "\n\n" + footer + "\n"
        parent = meta.get("parent") or None
        planned.append(Planned(
            key=f"local:{ident}", title=meta["title"], status=status, labels=labels,
            parent=f"local:{parent}" if parent else None, body=body, comments=comments,
            close=CLOSED_STATUSES.get(status), inlined=inlined, skipped=skipped, refs=refs, notes=notes,
        ))
    return planned, dropped


def linear_issues(items: list[dict], apps: set[str], repo_name: str, migrating: dict[str, set[str]]) -> list[Planned]:
    by_id = {i["id"]: i for i in items}
    keep = {i["id"] for i in items if i["statusType"] not in LINEAR_CLOSED}
    for ident in list(keep):
        parent = by_id[ident].get("parentId")
        while parent and parent in by_id:
            keep.add(parent)
            parent = by_id[parent].get("parentId")
    migrating["linear"] = keep

    def depth(ident: str) -> int:
        parent = by_id[ident].get("parentId")
        return 0 if parent not in keep else 1 + depth(parent)

    planned = []
    for ident in sorted(keep, key=lambda i: (depth(i), id_key(i))):
        item, refs, notes = by_id[ident], Refs(), []
        base = item["url"].split(f"/{ident}")[0]
        status = status_name(item["status"])
        if status not in OPEN_STATUSES and status not in CLOSED_STATUSES:
            status = LINEAR_TYPE_FALLBACK.get(item["statusType"], "Triage")
            notes.append(f"Linear status {item['status']!r} mapped by type to {status}")
        labels = base_labels(status)
        if item.get("priority", "").lower() in PRIORITIES:
            labels.append(f"priority:{item['priority'].lower()}")
        for name in item.get("labels", []):
            slug = name.strip().lower().replace(" ", "-")
            if slug == "database":
                labels.append("area:database")
            elif slug in TYPES:
                labels.append(f"type:{slug}")
            elif slug in apps:
                labels.append(f"app:{slug}")
            else:
                notes.append(f"Linear label {name!r} has no GitHub mapping")
        parent = item.get("parentId")
        if parent and parent not in keep:
            notes.append(f"Linear parent {parent} is not in the export, so no sub-issue link")
            parent = None
        comments = []
        for c in sorted(item.get("comments", []), key=lambda c: c["createdAt"]):
            head = f"**Linear comment** · {c.get('author') or 'unknown'} · {c['createdAt'][:10]}"
            comments.append(convert(f"{head}\n\n{c['body'].strip()}", "linear", migrating, repo_name, refs, base))
        footer = f"<sub>Migrated from Linear [{ident}]({item['url']})</sub>\n{marker('linear:' + ident)}"
        body = convert((item.get("description") or "").strip(), "linear", migrating, repo_name, refs, base) + "\n\n" + footer + "\n"
        planned.append(Planned(
            key=f"linear:{ident}", title=item["title"], status=status, labels=labels,
            parent=f"linear:{parent}" if parent else None, body=body, comments=comments,
            close=CLOSED_STATUSES.get(status), refs=refs, notes=notes,
        ))
    return planned


def review(plan: list[Planned]) -> None:
    for p in plan:
        problems = lint(PLACEHOLDER.sub("#1", p.body), "ticket")
        if problems:
            p.notes.append(f"body has {len(problems)} lint findings, first: {problems[0]}")
        if len(p.title) > 90 or re.search(r"[—–]", p.title):
            p.notes.append("title breaks the title rules: over 90 characters or a long dash")
        if len(p.body) > MAX_BODY:
            p.notes.append(f"body is {len(p.body)} characters, over the GitHub limit")
        for i, c in enumerate(p.comments):
            if len(c) + 60 > MAX_BODY:
                p.notes.append(f"comment {i} is {len(c)} characters, over the GitHub limit")


def build_plan(tdir: Path | None, linear: list[dict] | None, apps: set[str], repo_name: str) -> tuple[list[Planned], list[str]]:
    """Returns the ordered issues, parents first, and the attachments of closed local tickets left behind."""
    migrating: dict[str, set[str]] = {"local": set(), "linear": set()}
    local, dropped = local_tickets(tdir, apps, repo_name, migrating) if tdir else ([], [])
    plan = local + linear_issues(linear or [], apps, repo_name, migrating)
    review(plan)
    return plan, dropped


def render_plan(plan: list[Planned], dropped: list[str]) -> str:
    index = {p.key: n for n, p in enumerate(plan, 1)}
    out = []
    for n, p in enumerate(plan, 1):
        state = f"closed as {p.close}" if p.close else "open"
        out.append(f"[{n}] {p.key}, {state}, status {p.status}")
        out.append(f"    title: {p.title}")
        out.append(f"    labels: {', '.join(p.labels)}")
        out.append(f"    parent: {f'[{index[p.parent]}] {p.parent}' if p.parent else 'none'}")
        out.append(f"    comments: {len(p.comments)}")
        out.append(f"    attachments inlined: {'; '.join(p.inlined) or 'none'}")
        out.append(f"    attachments skipped: {'; '.join(p.skipped) or 'none'}")
        unresolved = sorted(set(p.refs.unresolved))
        out.append(f"    refs: {p.refs.converted} to #N, {p.refs.linked} to Linear links, {p.refs.prs} PR tags, "
                   f"{len(p.refs.unresolved)} unresolved{': ' + ', '.join(unresolved) if unresolved else ''}")
        out += [f"    note: {note}" for note in p.notes]
    by_status: dict[str, int] = {}
    for p in plan:
        by_status[p.status] = by_status.get(p.status, 0) + 1
    parents = {p.parent for p in plan if p.parent}
    out += [
        "",
        "Totals",
        f"  issues: {len(plan)} ({sum(p.key.startswith('local:') for p in plan)} local, {sum(p.key.startswith('linear:') for p in plan)} Linear)",
        "  by status: " + ", ".join(f"{s} {c}" for s, c in sorted(by_status.items(), key=lambda kv: -kv[1])),
        f"  closed on migration: {sum(1 for p in plan if p.close)}",
        f"  parents: {len(parents)}",
        f"  sub-issues: {sum(1 for p in plan if p.parent)}",
        f"  comments: {sum(len(p.comments) for p in plan)}",
        f"  attachments inlined: {sum(len(p.inlined) for p in plan)}",
        f"  attachments skipped: {sum(len(p.skipped) for p in plan)} binary, {len(dropped)} on closed local tickets",
        f"  refs to #N: {sum(p.refs.converted for p in plan)}",
        f"  refs to Linear links: {sum(p.refs.linked for p in plan)}",
        f"  PR tags converted: {sum(p.refs.prs for p in plan)}",
        f"  refs unresolved: {sum(len(p.refs.unresolved) for p in plan)}",
        f"  issues with notes: {sum(1 for p in plan if p.notes)}",
    ]
    if dropped:
        out.append("  left behind with closed local tickets: " + ", ".join(dropped))
    return "\n".join(out) + "\n"


class Executor:
    def __init__(self, gh: Gh, mapping_path: Path, pace: float):
        self.gh, self.path, self.pace = gh, mapping_path, pace
        self.map: dict[str, dict] = json.loads(mapping_path.read_text()) if mapping_path.exists() else {}

    def save(self) -> None:
        self.path.write_text(json.dumps(self.map, indent=1))

    def write(self, method: str, path: str, payload: dict) -> dict:
        result = self.gh.write(method, path, payload)
        time.sleep(self.pace)
        return result

    def resolve(self, text: str) -> str:
        return PLACEHOLDER.sub(lambda m: f"#{self.map[f'{m.group(1)}:{m.group(2)}']['number']}", text)

    def adopt_existing(self, plan: list[Planned]) -> None:
        wanted = {p.key for p in plan if p.key not in self.map}
        if not wanted:
            return
        issues = self.gh.read("issue", "list", "--repo", self.gh.repo, "--label", OWNER_LABEL, "--state", "all",
                              "--limit", "1000", "--json", "number,body")
        for issue in issues:
            m = re.search(r"<!-- migrated:((?:local|linear):DEV-[\d-]+) -->", issue.get("body") or "")
            if m and m.group(1) in wanted:
                self.map[m.group(1)] = {"number": issue["number"], "id": self.gh.issue(issue["number"])["id"]}
        self.save()

    def run(self, plan: list[Planned]) -> None:
        self.adopt_existing(plan)
        for p in plan:
            if p.key not in self.map:
                created = self.write("POST", "issues", {"title": p.title, "body": p.body, "labels": p.labels})
                self.map[p.key] = {"number": created["number"], "id": created["id"]}
                self.save()
                print(f"created #{created['number']} for {p.key}")
        for p in plan:
            state = self.map[p.key]
            if p.parent and not state.get("linked"):
                parent = self.map[p.parent]["number"]
                children = self.gh.api_get(f"issues/{parent}/sub_issues?per_page=100")
                if state["number"] not in {c["number"] for c in children}:
                    self.write("POST", f"issues/{parent}/sub_issues", {"sub_issue_id": state["id"]})
                state["linked"] = True
                self.save()
            if not state.get("body_resolved"):
                if PLACEHOLDER.search(p.body):
                    self.write("PATCH", f"issues/{state['number']}", {"body": self.resolve(p.body)})
                state["body_resolved"] = True
                self.save()
        for p in plan:
            state = self.map[p.key]
            if state.get("comments_posted", 0) < len(p.comments):
                existing = self.gh.api_get(f"issues/{state['number']}/comments?per_page=100", paginate=True)
                seen = {m for c in existing for m in re.findall(r"<!-- migrated:[^>]* -->", c["body"])}
                for i, text in enumerate(p.comments):
                    if marker(p.key, i) not in seen:
                        self.write("POST", f"issues/{state['number']}/comments", {"body": f"{self.resolve(text)}\n\n{marker(p.key, i)}"})
                    state["comments_posted"] = i + 1
                    self.save()
            if p.close and not state.get("closed"):
                self.write("PATCH", f"issues/{state['number']}", {"state": "closed", "state_reason": p.close})
                state["closed"] = True
                self.save()
        print(f"done: {len(plan)} issues in {self.path}")


def main_checkout() -> Path:
    common = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], capture_output=True, text=True)
    return Path(common.stdout.strip()).parent if common.returncode == 0 else Path.cwd()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="migrate_local.py", description=__doc__)
    ap.add_argument("--tickets-dir", type=Path, help="local tickets folder; default <main checkout>/tickets")
    ap.add_argument("--linear", type=Path, default=Path("/tmp/linear-open.json"), help="Linear export; skipped when absent")
    ap.add_argument("--apps-dir", type=Path, help="app folders for app: labels; default <tickets-dir>/../apps")
    ap.add_argument("--repo", help="owner/name; defaults to $TICKETS_REPO, then the origin remote")
    ap.add_argument("--plan-json", type=Path, default=Path("/tmp/ticket-migration-plan.json"))
    ap.add_argument("--mapping", type=Path, help="progress file for --execute; default <tickets-dir>/github-mapping.json")
    ap.add_argument("--execute", action="store_true", help="create the issues for real")
    ap.add_argument("--pace", type=float, default=1.0, help="seconds between writes under --execute")
    args = ap.parse_args(argv)
    try:
        tdir = args.tickets_dir or main_checkout() / "tickets"
        tdir = tdir if tdir.is_dir() else None
        linear = json.loads(args.linear.read_text()) if args.linear.exists() else None
        apps_dir = args.apps_dir or (tdir.parent / "apps" if tdir else Path("apps"))
        apps = {p.name for p in apps_dir.iterdir() if p.is_dir()} if apps_dir.is_dir() else set()
        repo = resolve_repo(args.repo)
        plan, dropped = build_plan(tdir, linear, apps, repo.split("/")[1])
        args.plan_json.write_text(json.dumps({"repo": repo, "issues": [asdict(p) for p in plan]}, indent=1, ensure_ascii=False))
        if not args.execute:
            print(f"repo: {repo}\nlocal: {tdir or 'none'}\nlinear: {args.linear if linear is not None else 'none'}\n")
            print(render_plan(plan, dropped), end="")
            print(f"\npayloads: {args.plan_json}")
            return 0
        if tdir is None and args.mapping is None:
            raise TicketError("--execute without a tickets folder needs --mapping")
        Executor(Gh(repo), args.mapping or tdir / "github-mapping.json", args.pace).run(plan)
    except TicketError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
