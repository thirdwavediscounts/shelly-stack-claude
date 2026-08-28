# benny

benny gives you two Claude Code routines for slack issue reports. one triages each report. the other reproduces confirmed bugs and may prepare a small draft fix.

the files in this directory are dormant setup and routine sources. they do not appear as slash skills.

## set it up

1. point Claude Code at [`FOR_AGENTS.md`](./FOR_AGENTS.md) and name the target repository.
2. let setup merge this whole directory into the target at `.claude/automations/benny/`. it must preserve destination-only files and review conflicts instead of overwriting local edits.
3. let setup add the marketplace with `/plugin marketplace add thirdwavediscounts/shelly-stack`, then enable shelly-stack in the target repository's `.claude/settings.json` for shared dependencies:

```json
{
	"enabledPlugins": {
		"shelly-stack@shelly-stack": true
	}
}
```

4. keep user-owned configuration outside the copied pack, for example in `.claude/benny/`. adapt [`configuration.example.yaml`](./templates/configuration.example.yaml) and [`feature-map.example.md`](./skills/reproduce-and-fix-issues/references/feature-map.example.md).
5. commit `.claude/settings.json`, `.claude/automations/benny/`, and any secret-free configuration before enabling either routine.
6. review each new routine draft or update existing routines in the routines list at claude.ai/code. then send a harmless test report and verify every source-channel post stays in the original thread.
