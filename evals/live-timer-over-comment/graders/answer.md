---
type: llm
weight: 1
---
Pass if the answer says comps already runs once a day at 12am, based on deploy/comps.timer or the commit that moved it, and says the "Runs every hour" comment in workers/comps.py is out of date. Fail if it says comps runs hourly.
