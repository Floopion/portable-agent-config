# portable-agent-config

An engineer's agent memory learns two things in the same sentence: how they like to work, and who they work for. "Keep commit messages short, the reviewers at this company skim" is both. The first part should follow you between tools and jobs. The second must never leave.

This repo is a convention and three scripts that keep them apart, plus one example of a second lesson: a rule that keeps being broken in memory stops being broken once it is a hook.

## Scopes

Every memory file says where it may go:

- `portable`: how you work. Safe to publish and carry to the next job.
- `work`: anything about your employer, its people, products, repos or tickets.
- `personal`: about you, but not for publishing.

Unsure means `work`. Only `portable` is ever exported.

```
---
name: "no-em-dash"
description: "one line"
metadata:
  type: feedback | project | reference | user
  scope: portable | work | personal
---
```

## One rule, twice

The rule first lived as a memory, [examples/no-em-dash.md](examples/no-em-dash.md):

```
Never use em dashes, en dashes or double hyphens in any output.
**Why:** they read as machine-written.
```

As prose it was still broken, again and again, in exactly the places it mattered most: commit messages and PR text. A memory is advice the agent weighs against everything else in its context. A hook is not advice. The idea of [hooks/guard.py](hooks/guard.py) fits in four lines:

```python
if POSTS_PROSE.search(command):            # git commit, gh pr, gh issue
    prose = command + "\n" + file_contents(tokens)   # includes --body-file text
    if DASHES.search(prose):
        deny("Em or en dash in text that will be committed or posted.")
```

Wired in through `settings.json`:

```json
"PreToolUse": [{ "matcher": "Bash",
  "hooks": [{ "type": "command", "command": "python3 ~/.claude/hooks/guard.py" }] }]
```

The agent now gets a refusal with a reason and rewrites the sentence. If the guard itself fails, it lets the call through.

## Install

1. Copy `hooks/guard.py` to `~/.claude/hooks/`.
2. Merge `hooks/settings.example.json` into `~/.claude/settings.json`.
3. Add `scope:` to your memory files, then export:

```
python3 export.py --memory ~/.claude/projects/*/memory --out ./memory
```

## Maintain

Before every push:

1. Run `export.py` again.
2. Copy `lint.local.example.json` to `lint.local.json` and list your employer, colleagues and projects. It is gitignored. Then run `python3 lint.py ./memory`.
3. Run a secret scanner over the repo, for example `gitleaks dir .`.
4. Read the diff by eye. A denylist only catches the names you remembered to list.

Python 3 standard library only. MIT licence.
