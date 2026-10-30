import json
import re
import sys

from transcript import entries, typed_prompt

STATUS = re.compile(r"^[\s>*_#+-]*(?:done|running|waiting on you)[*_]*:", re.I)
OFFER = re.compile(r"\b(?:want me to|would you like me to|shall i|should i go ahead|check back later|let me know if)\b", re.I)


def turn(path: str) -> list[dict]:
    log = entries(path)
    start = max((i for i, e in enumerate(log) if typed_prompt(e) is not None), default=-1)
    return [e for e in log[start + 1:] if e.get("type") == "assistant" and not e.get("isSidechain")]


def blocks(message: dict) -> list[dict]:
    content = message.get("message", {}).get("content")
    return content if isinstance(content, list) else []


def problem(event: dict) -> str | None:
    if event.get("stop_hook_active"):
        return None
    replies = turn(event["transcript_path"])
    if not any(b.get("type") == "tool_use" for e in replies for b in blocks(e)):
        return None
    text = event.get("last_assistant_message")
    if text is None:
        texts = [b.get("text", "") for e in replies for b in blocks(e) if b.get("type") == "text"]
        text = texts[-1] if texts else ""
    lines = [line for line in text.splitlines() if line.strip()]
    last = lines[-1] if lines else ""
    paragraph = text.strip().rsplit("\n\n", 1)[-1]
    if OFFER.search(paragraph):
        return (
            "Your reply ends by offering instead of doing. Do the reversible work now, "
            "then end with one status line: Done:, Running:, or Waiting on you:."
        )
    if not STATUS.match(last):
        return (
            "End the reply with one status line. Start it with Done: and the proof, "
            "Running: and what runs where, or Waiting on you: and the one thing you need."
        )
    return None


def main() -> None:
    try:
        reason = problem(json.load(sys.stdin))
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return
    if reason:
        json.dump({"decision": "block", "reason": reason}, sys.stdout)


main()
