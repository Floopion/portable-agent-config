#!/usr/bin/env python3
"""PreToolUse hook: block commit and PR text that breaks rules memory alone did not hold."""
import json
import os
import re
import shlex
import sys

DASHES = re.compile("[\u2014\u2013]|&mdash;|&ndash;|&#821[12];|&#x201[34];", re.I)
ATTRIBUTION = re.compile(r"Co-Authored-By:|Generated with ", re.I)
POSTS_PROSE = re.compile(r"\bgit\s+commit\b|\bgh\s+(pr|issue)\b")
FILE_FLAGS = ("-F", "--file", "--body-file")


def deny(reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))
    sys.exit(0)


def file_contents(tokens):
    """Text of files passed as a message or body, so prose in files is checked too."""
    paths = []
    for i, token in enumerate(tokens):
        if token in FILE_FLAGS and i + 1 < len(tokens):
            paths.append(tokens[i + 1])
        elif token.startswith(tuple(f + "=" for f in FILE_FLAGS)):
            paths.append(token.split("=", 1)[1])
    texts = []
    for path in paths:
        path = os.path.expanduser(path)
        if os.path.isfile(path):
            texts.append(open(path, encoding="utf-8", errors="ignore").read())
    return "\n".join(texts)


def check(command):
    if not POSTS_PROSE.search(command):
        return
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()
    prose = command + "\n" + file_contents(tokens)
    if DASHES.search(prose):
        deny("Em or en dash in text that will be committed or posted. "
             "Rewrite with a colon, a comma or two sentences.")
    if ATTRIBUTION.search(prose):
        deny("Commit or PR text carries a Co-Authored-By or 'Generated with' line. Remove it.")


def main():
    event = json.load(sys.stdin)
    if event.get("tool_name") == "Bash":
        check((event.get("tool_input") or {}).get("command", ""))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)  # never block work because the guard itself broke
