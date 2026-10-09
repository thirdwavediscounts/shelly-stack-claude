### Authoring or modifying a skill

**You own the skill's voice.**

1. Read `../../create-skill/SKILL.md` in full and follow it. The Skill tool refuses create-skill, so Read the file.
2. Validate the skill: frontmatter has `name` and `description`, referenced files exist, cross-skill links resolve.
3. If the change touches a step, trigger, or rule an agent must follow, run the **Eval** playbook (`playbooks/eval.md`) with one scenario where skipping the step looks reasonable. If the edit changes no instruction, mark this step `skip: wording only`.
4. Run **Opening a PR**.

When in doubt, delete. Keep only prose that changes a decision. Tell it to do the thing and skip the reason. Explain only when the rule is confusing without one. Match tone to scope. Point at structural sources (types, READMEs, config) per `../../principle-encode-lessons-in-structure/SKILL.md`. Delegate to other skills by path. Don't restate. When you keep hitting a workflow that no skill captures, propose a new skill.

**Reply:** summary of the skill, key design decisions, validation notes.
