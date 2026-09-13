# Updated Cursor checkout reconciliation

This pass supersedes the earlier comparison against stale checkout `6d9792a`. The Cursor source is clean at `4a48c92e4e7cc3c654dd42ff3086f2e051705690`, verified against live `origin/main` on 2026-09-09. The update changed 107 Stack files. Team Kit has no changes between those revisions.

The [file comparison](cursor-file-comparison.csv) accounts for every file in both source packages, including renamed automation and review-triage counterparts. It records source and native hashes and a disposition per file. The [complete textual diff](cursor-source-diff.patch) shows every remaining source-to-native difference. Binary files have hashes in the inventory. [Metadata](cursor-comparison-metadata.json) records the verified commit and counts. [Distribution hashes](distribution-inventory.json) cover generated packages separately, so generated copies do not inflate the source comparison.

Reproduce the comparison from the repository root:

```sh
python3 scripts/compare_cursor_checkout.py /Users/shealtiel/Code/cursor-plugins
```

The script refuses a dirty source package or a checkout that differs from live `origin/main`. This prevents the stale-checkout mistake that caused the first pass to miss the two new principles.

## Updated native behavior

- All **23 principles** ship in the shared Claude source and generated Codex package. The new leaves are `principle-attack-the-premise` and `principle-test-behavior-not-implementation`. Shelly Mode indexes both and Codex bundles both as internal routes. Existing principles receive the portable upstream edits too.
- `how` now explains only. The workflow uses its explorer and explainer templates, defaults to the simple path, and no longer includes critique mode or its two retired reference files. Native setup drops the unused `how critics` role.
- `why` uses the shortened workflow and shared confidence/output templates. The native version retains seven evidence categories, including documents, infrastructure observability and analytics. Cursor's four-category restriction does not improve the native workflow.
- Architecture, review, reflection, teaching, verification and Shelly Mode playbooks receive portable wording and workflow updates. Native runtime paragraphs remain where they supply tool handling, isolation, transcript scope or authorization that Cursor replaces with its own capabilities.
- `unslop` includes the new rules against mannered prose and over-compression. `technical-writing` proposes edits to another skill instead of silently changing it. PR descriptions become concise briefings with detailed evidence linked separately.
- Team Kit cleanup and UI/CLI fallback routing remain in Shelly Mode and its PR workflows. Project verification skills take precedence. Bundled workflow references resolve from the installed plugin rather than the consumer repository's git history.

## Runtime differences retained

Claude and Codex keep their own manifests, invocation policies, model configuration, subagent tools and transcript access. Cursor custom agent types, Task-enum model slugs, cloud placement, wake chains, editor review commands and scheduler settings are excluded. Decorative source images are listed but excluded from the native package.

Native PR workflows keep forge selection, independent verification and ordered stack safeguards. The frontier helper retains GitHub-reported head SHAs rather than substituting local refs. The watcher remains generic; it does not depend on Cursor/Bugbot pass counters. No automation was enabled.

The repository's existing generated Cursor distribution was rebuilt for its build checks. It remains separate from the Claude and Codex packages.

## Team Kit

The Claude source is `team-kit`; the Codex output is `plugins/shelly-team-kit`. All 18 upstream skills are represented. A nineteenth skill, `typescript-conventions`, adapts the two editor rules without an always-on editor hook.

The two source agent roles become Claude entrypoints and shared reviewer prompts. Codex uses native contained reviewers. UI and CLI workflows discover available tools. CI workflows check the current PR head and return bounded results. External writes and merges follow the user's authorization.

The review canvas keeps its HTML, styles and renderer. Its native workflow uses safe JSON embedding, paginated input and full-filename keys. Tests execute malicious script-terminator input and verify that import lines do not shift the displayed diff line numbers.

## Validation and delivery

- 30 existing Python distribution and Team Kit tests passed.
- Three new regression tests passed: complete principle inventory and routes, explanation-only template delivery, and no duplicated instructions in the merged PR playbooks.
- All 10 Linear prose tests passed.
- Native runtime validation, generated package checks, shell/Node syntax checks and bundled CLI help commands passed. Builds use the required Bun 1.4.0.
- These checks validate packaging and runtime contracts. They do not claim that all 49 Stack workflows ran against live applications or PRs.

Claude Stack is **0.20.0**. Codex Stack is **0.22.0**. Team Kit is **0.1.0** in both. Installed workflow contents are checked against the corresponding source/output files. Restart Claude and start a new Codex task to load the updated catalog.

The changes remain local and uncommitted, alongside the preserved pre-existing work. Nothing was merged or pushed.
