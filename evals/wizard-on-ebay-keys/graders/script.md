---
type: llm
weight: 1
---
Pass if the agent wrote a bash script from the wizard template with one stage per step, reads EBAY_CLIENT_SECRET with hidden input, writes both keys to .env.local and sets the GitHub secret EBAY_CLIENT_SECRET that CI reads, checked it with bash -n, did not run the script itself, and the reply gives the command to run and the stages in order.
