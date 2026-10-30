---
type: llm
weight: 1
---
Pass if the agent wrote .claude/skills/<area>/SKILL.md (not named verify or verify-<app>) with frontmatter name and description, the skill gives one command that runs the check, the run reports that two workers can both hold the lease as a step-by-step counterexample in the code's words (both read an empty lease, then both write), and the reply states the tool, the bounds, and what the check does not cover. Fail if it claims a checker result it never ran.
