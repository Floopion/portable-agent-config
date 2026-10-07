#!/usr/bin/env python3
"""Copy memories marked scope: portable into a folder you can publish."""
import argparse
import glob
import os
import re

HOME = os.path.expanduser("~")
HARNESS_ONLY = re.compile(r"^\s*(node_type|originSessionId|modified):.*\n", re.M)
LINK = re.compile(r"\[\[([^\]]+)\]\]")


def split_frontmatter(text):
    if not text.startswith("---\n") or text.count("---\n") < 2:
        return None, text
    _, fm, body = text.split("---\n", 2)
    return fm, body


def field(fm, key):
    m = re.search(rf'^\s*{key}:\s*"?(.*?)"?\s*$', fm, re.M)
    return m.group(1) if m else None


def memory_files(patterns):
    paths = []
    for pattern in patterns:
        for match in sorted(glob.glob(os.path.expanduser(pattern))):
            if os.path.isdir(match):
                paths += sorted(glob.glob(os.path.join(match, "*.md")))
            elif match.endswith(".md"):
                paths.append(match)
    return [p for p in paths if os.path.basename(p) != "MEMORY.md"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--memory", nargs="+", required=True, help="memory dirs or globs of them")
    parser.add_argument("--out", required=True, help="folder to write the export into")
    args = parser.parse_args()

    portable = {}
    for path in memory_files(args.memory):
        text = open(path, encoding="utf-8").read()
        fm, body = split_frontmatter(text)
        if fm is None or field(fm, "scope") != "portable":
            continue
        portable[field(fm, "name")] = (os.path.basename(path), fm, body, field(fm, "description"))

    keep_or_unlink = lambda m: m.group(0) if m.group(1) in portable else m.group(1)
    os.makedirs(args.out, exist_ok=True)
    index = ["# Memory index", ""]
    for name, (fname, fm, body, desc) in sorted(portable.items()):
        text = "---\n" + HARNESS_ONLY.sub("", fm) + "---\n" + LINK.sub(keep_or_unlink, body)
        with open(os.path.join(args.out, fname), "w", encoding="utf-8") as f:
            f.write(text.replace(HOME, "~"))
        index.append(f"- [{name}]({fname}): {desc}")
    with open(os.path.join(args.out, "MEMORY.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(index).replace(HOME, "~") + "\n")

    exported = {fname for fname, *_ in portable.values()} | {"MEMORY.md"}
    for stale in sorted(glob.glob(os.path.join(args.out, "*.md"))):
        if os.path.basename(stale) not in exported:
            print(f"stale: {stale} is no longer portable, delete it by hand")
    print(f"exported {len(portable)} portable memories to {args.out}")


if __name__ == "__main__":
    main()
