### Opening a PR

Invoked at the end of every other playbook. Add these steps to the todo list when a playbook reaches this one.

1. Run `/shelly-stack:deslop` on the scoped code diff.
2. Run the **unslop** skill over the diff's prose and comments.
3. For a nontrivial diff, spawn the `shelly-stack:thermo-nuclear-code-quality-review` agent on it. Fix or dismiss each finding with a reason.
4. When the work came from a Linear ticket, a spec, or a grilling session, spawn the `shelly-stack:spec-conformance-review` agent in the same message as step 3. Fetch the spec in the parent (the issue body and comments through the Linear MCP) and pass it with the diff. Keep its findings separate from the maintainability findings. A diff can pass one review and fail the other. Fix a missing requirement, drop unrequested behavior or record it as a scope change in the ticket, and fix or dismiss each wrong implementation with a reason.
5. Commit per **Commits**.
6. Run `/no-comments` before review.
7. Write the title and description per **Titles** and **Descriptions**. Open the PR per **Forge** and **Readiness**.
8. Before asking to merge, clear the list in **Before merge**.

Use the companion control skills only when the project verification skill lacks a suitable harness, following Shelly Mode's Companion skills section.

**Worktree.** Work from a git worktree off main. Subagents inherit it. Multiple `Agent` calls on the same branch each get their own worktree, or `git fetch && git reset --hard origin/<branch>` between them. Dirty branch with unrelated work: patch out, fresh worktree, apply. Snarled worktree: reset from main, redo minimally.

**Commits.** Commit liberally. Rebase into small, ordered commits before opening PRs. Each commit is a future PR: landable, ordered to tell the story. Amend when the fix belongs in a just-made commit. New commit when separable.

**PRs.** Write every PR title, PR description, and commit body with `/technical-writing`, then apply `/unslop`. Apply every technical-writing layer except Diátaxis. Use one word for each action, keep articles, and avoid `-ing` when a plain verb works.

**Titles.** Use Conventional Commits in the form `type(scope): subject`. Use `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, or `perf` as the type. Use the changed area, such as `shelly-stack` or `shelly-mode`, as the scope. Keep the subject short and imperative. Apply the same `/technical-writing` and `/unslop` pass as the body. Name a real symbol when one carries the change. For example, `fix(shelly-stack): retarget opening-a-pr babysit trigger`. Do not add a trailing period.

**Descriptions.** The PR body is a briefing, not the lab notebook. A reviewer who has the diff should learn why the change exists, what is out of scope, and how you proved the change works. The squash commit body is the PR body, so keep it short enough to read as one commit message.

Use these sections in order. Drop a section when it has nothing to say.

- `## Why`. State the intent and approach in one or two short paragraphs. Do not list SHAs or rebase genealogy. Do not add a "based on main" preamble.
- `## Scope`. Use bullets to list real symbols and paths. Name both sides of a rename or retarget. State what is in and out only when the boundary matters. Do not write a file-by-file essay.
- `## Tradeoffs`. Name only rejected alternatives that a reviewer would otherwise ask about. Skip this section when there was no real choice.
- `## Blast Radius`. In one to three sentences, name who or what the change touches and why the change is safe or risky. State the continuing cost if main stays red without the fix.
- `## Verification`. Name each real run path and its outcome. For a performance change, report one primary number with its unit in `before → after` form. Link the arena or swarm directory for the remaining evidence. Do not include sample-size methodology, swarm recitals, or metric tables.

After these sections, attach videos or screenshots when they prove a claim. Do not paste full SHAs, swarm or arena lane recitals, lever-correction essays, file-by-file checklists, or "CLEAN" verdicts. Put these details in a linked artifact. Do not use `## Summary` or `## Test plan` boilerplate. A commit body does not restate its subject.

**Forge.** Resolve the forge before the first PR operation and keep that choice for create, edit, view, watch, and merge. GitHub CLI (`gh`) is the default. If `command -v origin` succeeds and Origin can resolve the repository, prefer `origin pr ...`; if Origin is absent or cannot resolve the repository, stay on `gh` and record the fallback. Do not require Graphite (`gt`).

**Size and stacks.** Prefer five narrow PRs to one large PR. A stack is a base-branch chain. The root PR targets trunk. Each child branch rebases onto its parent's exact tip and its PR targets the parent branch. Create a child with `origin pr create --status open --base <parent-branch>` or `gh pr create --base <parent-branch>` according to the resolved forge. Retarget an existing child with `origin pr edit <pr> --base <parent-branch>` or `gh pr edit <pr> --base <parent-branch>`. Keep the ordered stack visible to reviewers by linking each PR body to its parent. Branch from trunk only for independent work. Rebase on trunk before substantial stack work.

**Readiness.** Open every PR ready, never as a draft. With Origin, pass `--status open`; with `gh`, omit `--draft`. Some PR tools default to draft, so set `draft: false` on every PR creation call. If a PR still opens as a draft, run `origin pr ready <number>` or `gh pr ready <number>` according to the resolved forge. Run `origin pr view <number>` or `gh pr view <number>` before you refer to PR status.

**Before merge.** Before asking to merge, list every open item you know of (follow-ups, review findings, deferred fixes) and every env var or config the deploy needs. Fold each into the PR, or get an explicit "leave it" from the user per item. The user reads "merge on green" as "nothing left", so an item still open at that point is a surprise, not a follow-up.

**Babysit.** Opening a PR does not start a babysit. Post the URL and keep building. Finish the phase or stack first. Run a separate babysit pass only when the user asks for one after the whole stack exists. A babysit for each new PR stalls the build and spends checks on commits that later waves restart. Push back when feedback drifts from intent.

A subagent that opens a PR runs `interrogate`, the **unslop** skill, and `/no-comments`. It returns the URL and does not babysit. Return to the parent.
