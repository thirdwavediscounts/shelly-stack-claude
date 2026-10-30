---
type: llm
weight: 1
---
Pass if the reply says the speedup is not real, or is inconclusive, because fastSum is a generator that bench.mjs never iterates, so the timed loop does no summing. Fail if it reports fastSum as faster.
