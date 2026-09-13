### Eval

**You own the experiment design. Plan, blind, run, synthesize.**

**Non-negotiables for blinding:**

- No `eval`, `test`, `judge`, `experiment`, `rubric`, `score`, `compare`, `benchmark`, `candidate`, or `arena` in any directory, file, or prompt the candidate sees.
- The candidate prompt looks like an organic user request. State the goal, not the meta.
- No chain-eliciting cues. Don't ask the candidate to list which skills, principles, or files they applied. Ask for design notes generally and grade chain-following from code shape, not self-report.
- Sanitize directory and slug names. Use project-shaped names a user might pick.
- Don't tell the candidate other candidates exist.
- The judge can know it's judging but sees outputs by sanitized label only, never by model name.
- Comparing two variants: one judge scores both sets in a single pass on one scale, blind to which set each came from.

**Steps:**

1. **Frame.** State what variant is under test and what behavior counts as success. Write the rubric (3-6 concrete criteria) for the judge only. Hold it back from candidates.
2. **Set up sanitized environments.** Per-candidate working dir with the variant in place. Plant any context an organic task would have: a project skeleton, the skills the candidate would naturally read.
3. **Author one organic prompt.** What a user would type. No leakage of what's being measured.
4. **Spawn N candidates** through the **[arena](../references/routed/arena/workflow.md)** skill's Phase B. Prefer distinct accepted model or reasoning-effort pairs when available; otherwise use fresh isolated runs. Respect the current child-slot capacity and refill a rolling window until all N have run. Each works in its own sanitized dir. Same prompt to each.
5. **Spawn one blinded judge** using a different accepted model or reasoning-effort pair from the candidates when available; otherwise use a fresh inherited reviewer per the **[arena](../references/routed/arena/workflow.md)** skill's Phase C. Judge sees outputs by sanitized label and the rubric, never a model name.
6. **Verify the chain from task evidence, not self-report.** Inspect each candidate's returned tool evidence plus native `list_threads` and `read_thread` when available. Otherwise use parent-provided narrow digests or exact candidate task paths. Never discover or scan unrelated `~/.codex/sessions/` records. Grade chain-following from the files candidates actually opened plus the resulting code shape, never from their own claims.
7. **Read every candidate output yourself** end to end. Compare to the judge's verdict. Disagreement means a model is biased or the rubric is ambiguous. Synthesize.

**Reply:** variant under test, rubric, per-candidate notes, judge's verdict, your synthesis, and a recommendation for whether to promote the variant.
