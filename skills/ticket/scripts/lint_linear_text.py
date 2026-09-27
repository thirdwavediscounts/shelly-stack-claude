#!/usr/bin/env python3
"""Lint Linear text (issue, project, comment) before save. Reads stdin, prints violations, exits 1 on any."""

from __future__ import annotations

import argparse
import re
import sys

ISSUE_TAG = re.compile(r"<issue\b[^>]*>.*?</issue>", re.S)
MENTION = re.compile(r"@@ISSUE@@|\bDEV-\d+\b")
MD_ISSUE_LINK = re.compile(r"\]\(<?https://linear\.app/[^)>\s]*/issue/")
DASH = re.compile(r"[—–]")
BOLD_LABEL = re.compile(r"^\s*(?:[-*]\s+|\d+\.\s+)?\*\*[^*\n]+?(?::\*\*|\*\*:)")
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
CURLY = re.compile(r"[‘’“”]")
EMOJI = re.compile(r"[\U0001F300-\U0001FAFF☀-➿]")
CHATBOT = re.compile(r"\b(I hope this helps|Let me know if|Certainly!|Of course!|Great question)", re.I)


def strip_code(text: str) -> list[tuple[int, str, str]]:
    """Return (line_no, cleaned, original) for prose lines. Inline code and issue tags are masked, fenced blocks dropped."""
    out = []
    fenced = False
    for n, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        cleaned = ISSUE_TAG.sub("@@ISSUE@@", line)
        out.append((n, re.sub(r"`[^`]*`", "`", cleaned), line))
    return out


def proper_nouns(lines: list[tuple[int, str, str]]) -> set[str]:
    """Words capitalized mid-sentence in prose count as proper nouns for the heading check."""
    found = set()
    for _, line, _ in lines:
        if HEADING.match(line):
            continue
        for m in re.finditer(r"(?<=[a-z0-9,;] )([A-Z][a-z]{3,})\b", line):
            found.add(m.group(1))
    return found


def title_case(words: list[str], proper: set[str]) -> bool:
    plain = [w for w in words if len(w) > 3 and w.isalpha() and w not in proper]
    caps = [w for w in plain if w[0].isupper() and w[1:].islower()]
    return len(plain) >= 2 and len(caps) == len(plain)


def lint(text: str, kind: str) -> list[str]:
    problems = []
    lines = strip_code(text)
    proper = proper_nouns(lines)
    if kind != "comment" and len(text.strip()) < 100:
        problems.append("1: too short for a description")
    for n, line, raw in lines:
        if len(MENTION.findall(line)) > 1:
            problems.append(f"{n}: more than one issue mention on a line: {raw.strip()[:80]}")
        if MD_ISSUE_LINK.search(line):
            problems.append(f"{n}: markdown link to an issue, use the <issue> tag or a bare DEV-N: {raw.strip()[:80]}")
        if DASH.search(line):
            problems.append(f"{n}: em or en dash: {raw.strip()[:80]}")
        if BOLD_LABEL.search(line):
            problems.append(f"{n}: bold label with colon: {raw.strip()[:80]}")
        if CURLY.search(line):
            problems.append(f"{n}: curly quote: {raw.strip()[:80]}")
        if CHATBOT.search(line):
            problems.append(f"{n}: chatbot phrase: {raw.strip()[:80]}")
        m = HEADING.match(line)
        if m:
            body = m.group(2)
            if EMOJI.search(body):
                problems.append(f"{n}: emoji in heading: {body[:80]}")
            if title_case(body.split(), proper):
                problems.append(f"{n}: title-case heading, use sentence case: {body[:80]}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", choices=["issue", "project", "comment"], default="issue")
    args = ap.parse_args()
    problems = lint(sys.stdin.read(), args.kind)
    for p in problems:
        print(p)
    print(f"{len(problems)} violation(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
