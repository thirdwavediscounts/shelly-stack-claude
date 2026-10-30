---
name: principle-prove-it-works
description: "Apply after completing a task, before declaring done. Verify against the real artifact (run the feature, read the actual value, inspect the diff), not a proxy, self-report, or 'it compiles.'"
user-invocable: false
---

# Prove It Works

Verify every task output by checking the real thing directly. Do not infer from proxies, self-reports, or "it compiles."

**Why:** Unverified work has unknown correctness. Indirect verification (file mtimes, output freshness, agent self-reports, cached screenshots) feels cheaper than direct observation. Acting on a wrong inference costs far more than checking the source.

Check the real thing, not a proxy:
- Check process liveness directly, not indirectly through derived state
- Read the actual value, not a cached or derived representation
- When verification fails, suspect the observation method before suspecting the system
- A "no difference" result proves safety only after you confirm the change reached the system (the server echoes the version or build it used). Otherwise report it as inconclusive
- A check proves only the build it ran against. After you move, rewrite, or reconfigure the thing, run the check again
- For a claim that needs a before-and-after proof, run the same check before and after the change and compare the outputs

Waiting is not verification. A cron tick, a timer, or a "bake" window proves nothing on its own. Trigger the path yourself on staging. When the check seems to need hours or days, invoke **compress-the-clock** and force or replay it before you put anything on a date.

## Numbers in the reply

Every count or rate names the query and the store it came from, and states its unit once (auctions vs searches, per run vs per hour). A number derived from logs is labelled as such and never stands alone. Read the number back from the store the user looks at.

## Script the check when you can

The strongest proof is a deterministic script that re-runs the same comparison, not a one-time eyeball. Write the script, run it, and keep its output as an artifact a reviewer can re-run instead of trusting your word.

Keep the artifact visible for the human. Show screenshots and images in the reply itself, not only as a file path. Commit it only for large or complex work where the trail has to be auditable later, like a big port or migration (the **show-me-your-work** skill).
