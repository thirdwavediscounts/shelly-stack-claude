# shelly-stack model configuration for cloud routines. Copied to ~/.claude/rules/ by the environment setup script.
# Values are plugin agent names (shelly-agent body + pinned model + effort) shipped in shelly-stack's agents/ folder.
# Spawn with `subagent_type: "<value>"` and omit the Agent `model` param.
#   fable = claude-fable-5-1   opus = claude-opus-5-5   sonnet = claude-sonnet-5
feature, refactoring: shelly-stack:shelly-sonnet-medium
bug-fix: shelly-stack:shelly-opus-high
perf-issue: shelly-stack:shelly-opus-high
hillclimb: shelly-stack:shelly-opus-medium
judgment and prose: shelly-stack:shelly-fable-high
hardest tasks: shelly-stack:shelly-fable-xhigh
how explorer: shelly-stack:shelly-sonnet-low
how explainer: shelly-stack:shelly-fable-high
how critics: shelly-stack:shelly-fable-high, shelly-stack:shelly-opus-high, shelly-stack:shelly-sonnet-medium
why investigators: shelly-stack:shelly-sonnet-low
why synthesizer: shelly-stack:shelly-fable-high
reflect tooling: shelly-stack:shelly-opus-medium
reflect judgment, divergent, synthesizer: shelly-stack:shelly-fable-high
arena runners: shelly-stack:shelly-fable-high, shelly-stack:shelly-opus-high, shelly-stack:shelly-sonnet-medium
arena cross-judge pool: shelly-stack:shelly-fable-high, shelly-stack:shelly-opus-high, shelly-stack:shelly-sonnet-high
swarm workers: shelly-stack:shelly-sonnet-medium
architect runners: shelly-stack:shelly-fable-high, shelly-stack:shelly-opus-high, shelly-stack:shelly-sonnet-medium
interrogate reviewers: shelly-stack:shelly-fable-high, shelly-stack:shelly-opus-high, shelly-stack:shelly-sonnet-high
