import json
import sys

from transcript import entries, typed_prompt

MAX_PROMPTS = 40
MAX_CHARS = 600
MAX_OUTPUT = 10_000
HEADER = "These are the user's earlier prompts in this session, oldest first. The decisions in them still stand."


def main() -> None:
    try:
        log = entries(json.load(sys.stdin)["transcript_path"])
        lines = [f"- {p[:MAX_CHARS]}" for p in map(typed_prompt, log) if p][-MAX_PROMPTS:]
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return
    while lines and len("\n".join([HEADER, *lines])) > MAX_OUTPUT:
        lines.pop(0)
    if lines:
        print("\n".join([HEADER, *lines]))


main()
