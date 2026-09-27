#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lint_linear_text import lint  # noqa: E402

GOOD = """Both syncs book any refund as REFUNDED, so a partial refund reads as a full return. Define the signal at the line.

## Evidence

* Argus `ebay-sales-sync` marks a line REFUNDED when `item.refunds` has one or more entries.
* Only five readers distinguish partial from full.

| Set | Rows | Net kept |
| -- | -- | -- |
| No return record | 52 | $6,919 |

## Do

1. Define partial refund as `refund_price > 0 AND refund_price < sale_price`.

## Acceptance

- [ ] Consumer table signed by Sean before any edit.

## Links

* Parent, spec item 4: <issue id="9f2ce714" href="https://linear.app/x/issue/DEV-158/a">DEV-158</issue>
* Needs-disposition queue: DEV-176
"""

BAD = """Scope

Phases 0 to 7 (<issue id="a" href="https://linear.app/x/issue/DEV-153/a">DEV-153</issue> to <issue id="b" href="https://linear.app/x/issue/DEV-160/b">DEV-160</issue>), then DEV-208.

**Performance:** the repack shrank the heap — from 1,177 MB to 39 MB.

## Acceptance Criteria

See [DEV-176](<https://linear.app/x/issue/DEV-176/a>) for the queue. “Great question”, I hope this helps!
"""


class LintTest(unittest.TestCase):
    def test_clean_text_passes(self):
        self.assertEqual(lint(GOOD, "issue"), [])

    def test_chained_mentions(self):
        self.assertTrue(any("more than one issue mention" in p for p in lint(BAD, "issue")))

    def test_markdown_issue_link(self):
        self.assertTrue(any("markdown link to an issue" in p for p in lint(BAD, "issue")))

    def test_dash_and_bold_label(self):
        problems = lint(BAD, "issue")
        self.assertTrue(any("em or en dash" in p for p in problems))
        self.assertTrue(any("bold label" in p for p in problems))

    def test_title_case_heading(self):
        self.assertTrue(any("title-case heading" in p for p in lint(BAD, "issue")))

    def test_sentence_case_with_identifiers_passes(self):
        text = "x" * 100 + "\n## Why the flag is wrong\n## Unindexed foreign keys\n## Merged PRs\n## Phase 7b grant hygiene\n"
        self.assertEqual([p for p in lint(text, "issue") if "heading" in p], [])

    def test_proper_noun_headings_pass(self):
        text = "Every body you save to Linear follows the shape. Sean reads it.\n" + "x" * 60 + "\n## Writing to Linear\n## Argus Engine defects\n"
        self.assertEqual([p for p in lint(text, "issue") if "heading" in p], [])

    def test_curly_quotes_and_chatbot(self):
        problems = lint(BAD, "issue")
        self.assertTrue(any("curly quote" in p for p in problems))
        self.assertTrue(any("chatbot phrase" in p for p in problems))

    def test_code_is_ignored(self):
        text = "x" * 100 + "\n```sql\n-- DEV-1 DEV-2 — fine\n```\nSee `DEV-3 DEV-4 —` inline.\n"
        self.assertEqual(lint(text, "issue"), [])

    def test_short_comment_allowed(self):
        self.assertEqual(lint("2026-09-02. Rewrote the description.", "comment"), [])
        self.assertTrue(any("too short" in p for p in lint("short", "issue")))


if __name__ == "__main__":
    unittest.main()
