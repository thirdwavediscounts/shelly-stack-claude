### Feature

**You own the design. Plan, review, verify.** Delegate implementation. Stay in the lead.

1. Call the Skill tool with `shelly-stack:how` on the affected subsystem. No skip. Reading the files yourself does not replace the call.
2. If the change adds or changes a type, an exported signature, or a module boundary, call the Skill tool with `shelly-stack:architect` for parallel design exploration. Otherwise mark it `skip: one function body`. Two or more open product decisions found while grounding go to the user before the sketch, when the user is in the session. Call the Skill tool with `shelly-stack:grilling` and ask them as one round. When the user is away, pick the recommended answer, record it, and keep going. New domain terms go through the **domain-modeling** skill. Do not fold the design decision silently into implementation.
3. Write the throughput checkpoint as four todo items. A dimension that genuinely does not apply (single file, no fan-out) keeps its item with `n/a: <reason>` rather than being dropped:
   - **Blocking first steps.** Gates run before fan-out.
   - **Independent workstreams.** Disjoint files, services, or layers parallelize. Shared writes serialize.
   - **Shared mutable state.** Default to splitting the target (`../../principle-separate-before-serializing-shared-state/SKILL.md`). Serialize only for real invariants.
   - **Smallest safe decomposition.** If one worker is best, name why.
4. Delegate code-writing to a subagent using your configured feature model (default `sonnet`) with a specific scope (file paths, named data shape and its organizing structure per `../../principle-model-the-domain/SKILL.md`, such as a state machine over scattered booleans, a table/registry over branching, a typed model over repeated shape assumptions, chosen before the delegate writes logic, and success criteria); review its diff yourself. When the implementation admits multiple valid shapes (error handling, abstraction layer, test structure), delegate via the **arena** skill instead so the runners surface the alternatives and the cross-judge guards the pick. No skip at any size. Laziness Protocol does not override it, because the gain is review separation, not lines saved. A subagent can spawn its own delegate. One that cannot owns the diff itself with the same review separation, and never idles waiting on a nested agent. Comments per **Comments**. Surgical edits, re-ground against the source for upstream-derived files. Port shared-primitive improvements to all consumers and verify each. Commit freely.
5. Verify on the matching surface. "Inconclusive" or wrong-surface is not a pass. Flag it. For a claim that needs a baseline-versus-treatment proof, invoke **verify-this**. When the repo has a smoke suite covering the surface, invoke **run-smoke-tests**.
6. Rebase into small, ordered commits. Stack follow-ups.
   Use `../../principle-sequence-verifiable-units/SKILL.md`, building, verifying, and committing each small unit before the next.
7. If the design is contested (two or more architect runners disagreed, or the user pushed back on the design), call the Skill tool with `shelly-stack:interrogate`.
8. Run **Opening a PR**.

Code-coupled work (one feature, one migration) goes to a single owner with the checkpoint inline. That owner fans out internally after the blocking phase. Parent-level fan-out is for slices that produce independent artifacts (audits, cross-subsystem investigations, competing experiments). Rewrite the checkpoint at phase boundaries. Spawn a fresh owner rather than chaining interrupts.

**Reply:** what you built, what you chose and why, the throughput checkpoint, open decisions. Tables for design alternatives.
