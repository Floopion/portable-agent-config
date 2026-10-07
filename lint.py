#!/usr/bin/env python3
"""Fail if an export holds anything that must stay local. Run before every push."""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HOME_PATH = re.compile(r"/Users/[^/\s]+|/home/[^/\s]+|[A-Za-z]:\\Users\\[^\\\s]+")
HARNESS_ONLY = re.compile(r"^\s*(node_type|originSessionId|modified):", re.M)
LINK = re.compile(r"\[\[([^\]]+)\]\]")


def load_denylist():
    path = os.path.join(HERE, "lint.local.json")
    if not os.path.isfile(path):
        sys.exit("lint.local.json missing next to lint.py: copy lint.local.example.json "
                 "and list your employer, colleague and project names in it")
    return [re.compile(p) for p in json.load(open(path, encoding="utf-8")).get("deny_regex", [])]


def frontmatter(text):
    if not text.startswith("---\n") or text.count("---\n") < 2:
        return None
    return text.split("---\n", 2)[1]


def main():
    if len(sys.argv) != 2 or not os.path.isdir(sys.argv[1]):
        sys.exit("usage: python3 lint.py <dir>")
    root = sys.argv[1]
    denylist = load_denylist()
    problems = []

    files = [p for p in glob.glob(os.path.join(root, "**", "*"), recursive=True)
             if os.path.isfile(p) and f"{os.sep}.git{os.sep}" not in p
             and ".local." not in os.path.basename(p)]
    names, links = set(), []
    for path in files:
        rel = os.path.relpath(path, root)
        text = open(path, encoding="utf-8", errors="ignore").read()
        for i, line in enumerate(text.splitlines(), 1):
            for pattern in denylist:
                for m in pattern.finditer(line):
                    problems.append(f"{rel}:{i}: denylisted {m.group(0)!r}")
            for m in HOME_PATH.finditer(line):
                problems.append(f"{rel}:{i}: absolute home path {m.group(0)!r}")
        fm = frontmatter(text) if rel.endswith(".md") else None
        if fm is None or os.path.basename(path) == "MEMORY.md":
            continue
        scope = re.search(r'^\s*scope:\s*"?(\w+)', fm, re.M)
        if not scope or scope.group(1) != "portable":
            problems.append(f"{rel}: scope is {scope.group(1) if scope else 'missing'}, not portable")
        if HARNESS_ONLY.search(fm):
            problems.append(f"{rel}: harness-only frontmatter key (session id or timestamp)")
        name = re.search(r'^name:\s*"?(.*?)"?\s*$', fm, re.M)
        if name:
            names.add(name.group(1))
        links += [(rel, link) for link in LINK.findall(text)]

    problems += [f"{rel}: dangling link [[{link}]]" for rel, link in links if link not in names]
    print("\n".join(problems) if problems else "lint clean")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
