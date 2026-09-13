# Build the Lever

For non-trivial implementation work, build the smallest tool that makes the authorized change repeatable. For a read-only analysis, use existing commands or an inline probe and do not create repository files.

**Why:** Two payoffs. Throughput: a codemod, generator, or script does the work the same way every time and reruns for free. Confidence: the tool is one artifact a reviewer can read and rerun to check the work. Hand-done changes can only be re-verified by redoing them. A deterministic script turns "trust me" into "run this".

**Pattern:** Build a lever only when local edits are in scope. In a read-only task, the lever is an existing command, in-memory query, or stdout-only check.

- Do the first unit by hand to learn the recipe, then build the tool. Prove it by rerunning it on that unit and diffing against your hand-done version. Make the lever safe to rerun.
- Use a codemod or script for authorized edits and a generator for repetitive files. For read-only analysis, prefer an existing query or a check that writes only to stdout.
- A deterministic lever beats fan-out. If the tool can process every unit in one pass, run it yourself. Don't fan out delegates to hand-apply what a script can do.
- When you fan work out to subagents, write the lever as a skill they all read: the recipe, the verification contract, and the do-not-touch fences in one artifact. Keep it outside the delegates' write scope so they can't quietly edit the contract.
- In implementation scope, applying this principle normally produces a codemod, script, generator, or delegate skill. In read-only scope, producing a file would violate the task; show the exact existing or inline command instead.
- Commit the lever only when the current request explicitly authorizes commits. Otherwise leave the verified change in the working tree.

**Balance:** The bar is triviality, not repetition. A one-off still earns a lever when the lever is what makes the work checkable. Per the [Laziness Protocol](../principle-laziness-protocol/workflow.md), build the smallest script that does or proves the job, never a framework.

Distinct from [Encode Lessons in Structure](../principle-encode-lessons-in-structure/workflow.md), which makes a recurring instruction a durable guardrail. This is throughput and reviewability on the work in front of you. For scripting the verification itself, see [Prove It Works](../principle-prove-it-works/workflow.md).
