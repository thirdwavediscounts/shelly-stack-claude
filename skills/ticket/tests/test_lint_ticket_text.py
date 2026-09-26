#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from lint_ticket_text import lint  # noqa: E402

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

* Parent, spec item 4: #158
* Needs-disposition queue: #176
* Branch `sean/dev-176-queue`, from https://linear.app/t/issue/DEV-176/queue
"""

BAD = """Scope

**Performance:** the repack shrank the heap — from 1,177 MB to 39 MB.

## Acceptance Criteria

See the queue. “Great question”, I hope this helps!
"""


class LintTest(unittest.TestCase):
    def test_clean_text_passes(self):
        self.assertEqual(lint(GOOD, "ticket"), [])

    def test_dash_and_bold_label(self):
        problems = lint(BAD, "ticket")
        self.assertTrue(any("em or en dash" in p for p in problems))
        self.assertTrue(any("bold label" in p for p in problems))

    def test_title_case_heading(self):
        self.assertTrue(any("title-case heading" in p for p in lint(BAD, "ticket")))

    def test_sentence_case_with_identifiers_passes(self):
        text = "x" * 100 + "\n## Why the flag is wrong\n## Unindexed foreign keys\n## Merged PRs\n## Phase 7b grant hygiene\n"
        self.assertEqual([p for p in lint(text, "ticket") if "heading" in p], [])

    def test_proper_noun_headings_pass(self):
        text = "Every ticket body follows the shape. Sean reads it before Argus ships.\n" + "x" * 60 + "\n## Argus Engine defects\n"
        self.assertEqual([p for p in lint(text, "ticket") if "heading" in p], [])

    def test_curly_quotes_and_chatbot(self):
        problems = lint(BAD, "ticket")
        self.assertTrue(any("curly quote" in p for p in problems))
        self.assertTrue(any("chatbot phrase" in p for p in problems))

    def test_code_is_ignored(self):
        text = "x" * 100 + "\n```sql\n-- DEV-1 DEV-2 — fine\n```\nSee `a — b` inline.\n"
        self.assertEqual(lint(text, "ticket"), [])

    def test_dev_ids_in_prose_are_refused(self):
        problems = lint("x" * 100 + "\nBlocked by DEV-2-6 until the trigger fix lands.\n", "ticket")
        self.assertEqual(problems, ["2: ticket reference DEV-2-6, use the issue number #N: Blocked by DEV-2-6 until the trigger fix lands."])

    def test_migration_footer_is_exempt(self):
        text = "x" * 100 + "\n<sub>Migrated from local ticket DEV-2</sub>\n<!-- migrated:local:DEV-2 -->\n"
        self.assertEqual(lint(text, "ticket"), [])

    def test_short_comment_allowed(self):
        self.assertEqual(lint("2026-09-02. Rewrote the description.", "comment"), [])
        self.assertTrue(any("too short" in p for p in lint("short", "ticket")))


if __name__ == "__main__":
    unittest.main()
