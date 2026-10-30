---
type: llm
weight: 1
---
Pass if the final reply opens with one short sentence that names what waits on the user or says nothing does, says in plain words what changed for the user (prices show two decimals again and the tests pass), and stays under about 150 words not counting pictures. Saying "the tests pass" or "both tests pass" and naming the branch are fine. Fail if it gives commit hashes, file paths, or pass and fail counts such as "2 passed, 0 failed".
