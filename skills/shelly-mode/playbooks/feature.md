### Feature

**You own the design. Plan, review, verify.** Delegate implementation. Stay in the lead.

1. Look first. Read the code the change touches and the sibling that already does something like it, and check the live system per the look-first trigger in Shelly Mode. Call the Skill tool with `shelly-stack:how` only when the change crosses subsystems you have not read. Then list what the existing system already guarantees: its schedule, its time windows, what it already filters or deletes, and the pattern its siblings use. The design names which of those it relies on. Every check or guard beyond them names a real event those guarantees still allow, backed by a count or a log line. "This could happen" is not enough. Reuse the existing pattern unless you can name why it fails here.
2. If the change adds or changes a type, an exported signature, or a module boundary, call the Skill tool with `shelly-stack:architect` for parallel design exploration. Otherwise mark it `skip: one function body`. Two or more open product decisions found while grounding go to the user before the sketch, when the user is in the session. Call the Skill tool with `shelly-stack:grilling` and ask them as one round. When the user is away, pick the recommended answer, record it, and keep going. New domain terms go through the **domain-modeling** skill. Do not fold the design decision silently into implementation. Before the sketch, Read the principle for each case that applies:
   - New types, validation, or error handling: `../../principle-type-system-discipline/SKILL.md` and `../../principle-boundary-discipline/SKILL.md`.
   - A job, step, or loop that can crash and retry: `../../principle-make-operations-idempotent/SKILL.md`.
   - A new requirement in an existing design: `../../principle-redesign-from-first-principles/SKILL.md`.
   - A product or UX tradeoff: `../../principle-experience-first/SKILL.md`.
3. Write the throughput checkpoint as four todo items. A dimension that genuinely does not apply (single file, no fan-out) keeps its item with `n/a: <reason>` rather than being dropped:
   - **Blocking first steps.** Gates run before fan-out.
   - **Independent workstreams.** Disjoint files, services, or layers parallelize. Shared writes serialize.
   - **Shared mutable state.** Default to splitting the target (`../../principle-separate-before-serializing-shared-state/SKILL.md`). Serialize only for real invariants.
   - **Smallest safe decomposition.** If one worker is best, name why.
4. On a small task, write the change yourself. Otherwise delegate code-writing to a subagent using your configured feature model (default `sonnet`) with a specific scope (file paths, named data shape and its organizing structure per `../../principle-model-the-domain/SKILL.md`, such as a state machine over scattered booleans, a table/registry over branching, a typed model over repeated shape assumptions, chosen before the delegate writes logic, and success criteria); review its diff yourself. When the user asked for a bakeoff, delegate via the **arena** skill instead. A subagent can spawn its own delegate. One that cannot owns the diff itself with the same review separation, and never idles waiting on a nested agent. Comments per **Comments**. Surgical edits, re-ground against the source for upstream-derived files. Port shared-primitive improvements to all consumers and verify each. Commit freely. When one edit repeats across many files, Read `../../principle-build-the-lever/SKILL.md` and script it. Before you or the delegate writes a test, Read `../../principle-test-behavior-not-implementation/SKILL.md`.
5. Read `../../principle-prove-it-works/SKILL.md` now. Verify on the matching surface. "Inconclusive" or wrong-surface is not a pass. Flag it. When the repo has a smoke suite covering the surface, run it.
6. Rebase into small, ordered commits, one per improvement, in one PR. Fold in the follow-ups the ask needs. List the rest under **Before merge** in Opening a PR.
   Use `../../principle-sequence-verifiable-units/SKILL.md`, building, verifying, and committing each small unit before the next.
7. If the user asks to challenge the design, call the Skill tool with `shelly-stack:interrogate`.
8. Run **Opening a PR**.

Code-coupled work (one feature, one migration) goes to a single owner with the checkpoint inline. That owner fans out internally after the blocking phase. Parent-level fan-out is for slices that produce independent artifacts (audits, cross-subsystem investigations, competing experiments). Rewrite the checkpoint at phase boundaries. Spawn a fresh owner rather than chaining interrupts.

**Reply:** what you built, what you chose and why, the throughput checkpoint, open decisions. Tables for design alternatives.
