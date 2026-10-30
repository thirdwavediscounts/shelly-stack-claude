import json
import re

REMINDER = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)
COMMAND_ARGS = re.compile(r"<command-args>(.*?)</command-args>", re.S)
WRAPPER = re.compile(r"<(?:task-notification|local-command-\w+|command-name|command-message|bash-\w+"
                     r"|artifact-content-authored-by-others)\b")


def entries(path: str) -> list[dict]:
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def typed_prompt(entry: dict) -> str | None:
    if entry.get("type") != "user" or entry.get("isSidechain") or entry.get("isMeta"):
        return None
    if entry.get("toolUseResult") or entry.get("isCompactSummary"):
        return None
    origin = entry.get("origin")
    human = isinstance(origin, dict) and origin.get("kind") == "human"
    if isinstance(origin, dict) and not human:
        return None
    content = entry.get("message", {}).get("content")
    if isinstance(content, list):
        if any(block.get("type") == "tool_result" for block in content):
            return None
        content = "\n".join(block.get("text", "") for block in content if block.get("type") == "text")
    if not isinstance(content, str):
        return None
    args = COMMAND_ARGS.search(content)
    if args:
        return args.group(1).strip()
    text = REMINDER.sub("", content).strip()
    if not text or text.startswith("[Request interrupted") or WRAPPER.match(text):
        return None
    if text.startswith("<") and not human:
        return None
    return text
